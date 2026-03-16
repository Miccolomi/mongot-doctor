"""
Report builder — three output formats:
  text     → proprietary ASCII (Slack, terminal, support tickets)
  markdown → GitHub issues, Confluence, Notion
  json     → integrations, CI pipelines, alerting tools
"""

from datetime import datetime, timezone


# ── Helpers ───────────────────────────────────────────────────────────────────

def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def _health(findings: list) -> tuple[str, int, int, int]:
    crits  = [f for f in findings if f.get("status") == "crit"]
    warns  = [f for f in findings if f.get("status") == "warn"]
    passes = [f for f in findings if f.get("status") == "pass"]
    h = "CRITICAL" if crits else "DEGRADED" if warns else "HEALTHY"
    return h, len(crits), len(warns), len(passes)


def _ms(sec) -> str:
    if not sec:
        return "—"
    return f"{round(float(sec) * 1000)}ms"


# ── Text (proprietary) ────────────────────────────────────────────────────────

def build_text(data: dict, findings: list) -> str:
    W   = 58
    bar = "━" * W

    def sec(title):
        return f"\n── {title} " + "─" * (W - len(title) - 4)

    health, nc, nw, np_ = _health(findings)
    icon = {"CRITICAL": "🔴", "DEGRADED": "🟡", "HEALTHY": "🟢"}[health]

    L = []
    L += [bar, "  MONGODB SEARCH — STATUS REPORT", f"  {_ts()}", bar]
    L += [f"\nCLUSTER HEALTH: {icon} {health}  ({nc} critical · {nw} warnings · {np_} passed)"]

    # Pods
    pods = (data or {}).get("mongot_pods") or []
    L.append(sec("PODS"))
    if pods:
        for p in pods:
            restarts = p.get("total_restarts", 0)
            ready    = "READY" if p.get("all_ready") else "NOT READY"
            flag     = " ⚠" if restarts > 0 else ""
            L.append(f"  {p['name']:<42} {p.get('phase','?'):<10} {ready}  Restarts: {restarts}{flag}")
            if p.get("node"):
                L.append(f"    Node: {p['node']}")
    else:
        L.append("  No pods found.")

    # Search metrics
    prom_all = (data or {}).get("mongot_prometheus") or {}
    L.append(sec("SEARCH METRICS"))
    if prom_all:
        for pod_name, prom in prom_all.items():
            cats = prom.get("categories", {})
            sc   = cats.get("search_commands", {})
            idx  = cats.get("indexing", {})
            sync = (idx.get("initial_sync_in_progress") or 0) > 0
            L.append(f"  Pod: {pod_name}")
            L.append(f"    $search QPS:        {sc.get('search_qps', 0):.2f}/s")
            L.append(f"    $search avg lat.:   {_ms(sc.get('search_avg_latency_sec'))}")
            L.append(f"    $vectorSearch QPS:  {sc.get('vectorsearch_qps', 0):.2f}/s")
            L.append(f"    Indexing lag:       {idx.get('change_stream_lag_sec', 0):.1f}s")
            L.append(f"    Initial sync:       {'Yes ⚠' if sync else 'No'}")
    else:
        L.append("  No Prometheus data available.")

    # Oplog
    oplog = (data or {}).get("oplog_info") or {}
    if oplog.get("window_hours"):
        L.append(sec("OPLOG"))
        L.append(f"  Window: {oplog['window_hours']}h  ·  Head: {oplog.get('head_time', '—')}")

    # SRE Advisor
    crits  = [f for f in findings if f.get("status") == "crit"]
    warns  = [f for f in findings if f.get("status") == "warn"]
    passes = [f for f in findings if f.get("status") == "pass"]
    L.append(sec("SRE ADVISOR"))
    for f in crits:
        L.append(f"  ✖ [CRIT] {f['title']} — {f['value']}")
    for f in warns:
        L.append(f"  ⚠ [WARN] {f['title']} — {f['value']}")
    for f in passes:
        L.append(f"  ✔ {f['title']}")
    if not findings:
        L.append("  No advisor data yet.")

    # Search indexes
    idxs = (data or {}).get("search_indexes") or []
    L.append(sec("SEARCH INDEXES"))
    if idxs:
        for idx in idxs:
            status = idx.get("status", "?")
            sflag  = " ⚠" if status not in ("READY", "ready") else ""
            qflag  = "  (not queryable ✖)" if not idx.get("queryable", True) else ""
            L.append(f"  {idx['ns']} / {idx['name']} [{idx.get('type','?')}] {status}{sflag}{qflag}")
    else:
        L.append("  No Search indexes found.")

    # Recommendations
    recs = [f["doc"] for f in crits + warns if f.get("doc")]
    if recs:
        L.append(sec("RECOMMENDATIONS"))
        for r in recs:
            L.append(f"  → {r}")

    # Errors
    errors = (data or {}).get("global_errors") or []
    if errors:
        L.append(sec("ERRORS DETECTED"))
        for e in errors:
            L.append(f"  ! {e}")

    L += [f"\n{bar}", "  mongot-monitor · github.com/Miccolomi/mongot-monitor", bar]
    return "\n".join(L)


# ── Markdown ──────────────────────────────────────────────────────────────────

def build_markdown(data: dict, findings: list) -> str:
    health, nc, nw, np_ = _health(findings)
    icon = {"CRITICAL": "🔴", "DEGRADED": "🟡", "HEALTHY": "🟢"}[health]

    crits  = [f for f in findings if f.get("status") == "crit"]
    warns  = [f for f in findings if f.get("status") == "warn"]
    passes = [f for f in findings if f.get("status") == "pass"]

    L = []
    L += [f"# MongoDB Search — Status Report", f"*Generated: {_ts()}*\n"]
    L += [f"## {icon} Cluster Health: {health}",
          f"> **{nc} critical** · **{nw} warnings** · **{np_} passed**\n"]

    # Pods
    pods = (data or {}).get("mongot_pods") or []
    L.append("## Pods\n")
    if pods:
        L += ["| Pod | Phase | Ready | Restarts | Node |",
              "|:----|:------|:------|:---------|:-----|"]
        for p in pods:
            restarts = p.get("total_restarts", 0)
            r_str    = f"{restarts} ⚠" if restarts > 0 else str(restarts)
            L.append(f"| `{p['name']}` | {p.get('phase','?')} | {'✔' if p.get('all_ready') else '✖'} | {r_str} | {p.get('node','—')} |")
    else:
        L.append("*No pods found.*")
    L.append("")

    # Search metrics
    prom_all = (data or {}).get("mongot_prometheus") or {}
    L.append("## Search Metrics\n")
    if prom_all:
        for pod_name, prom in prom_all.items():
            cats = prom.get("categories", {})
            sc   = cats.get("search_commands", {})
            idx  = cats.get("indexing", {})
            sync = (idx.get("initial_sync_in_progress") or 0) > 0
            L += [f"**{pod_name}**\n",
                  "| Metric | Value |", "|:-------|:------|",
                  f"| `$search` QPS | `{sc.get('search_qps', 0):.2f}/s` |",
                  f"| `$search` avg latency | `{_ms(sc.get('search_avg_latency_sec'))}` |",
                  f"| `$vectorSearch` QPS | `{sc.get('vectorsearch_qps', 0):.2f}/s` |",
                  f"| Indexing lag | `{idx.get('change_stream_lag_sec', 0):.1f}s` |",
                  f"| Initial sync | `{'Yes ⚠' if sync else 'No'}` |", ""]
    else:
        L.append("*No Prometheus data available.*\n")

    # Oplog
    oplog = (data or {}).get("oplog_info") or {}
    if oplog.get("window_hours"):
        L += ["## Oplog\n",
              f"- Window: **{oplog['window_hours']}h**",
              f"- Head: `{oplog.get('head_time','—')}`\n"]

    # SRE Advisor
    L.append("## SRE Advisor\n")
    for f in crits:
        L.append(f"- 🔴 **[CRIT] {f['title']}** — {f['value']}")
    for f in warns:
        L.append(f"- 🟡 **[WARN] {f['title']}** — {f['value']}")
    for f in passes:
        L.append(f"- ✅ {f['title']}")
    if not findings:
        L.append("*No advisor data yet.*")
    L.append("")

    # Search indexes
    idxs = (data or {}).get("search_indexes") or []
    L.append("## Search Indexes\n")
    if idxs:
        L += ["| Collection | Index | Type | Status | Queryable |",
              "|:-----------|:------|:-----|:-------|:----------|"]
        for idx in idxs:
            status = idx.get("status", "?")
            s_str  = f"⚠ {status}" if status not in ("READY", "ready") else status
            q      = "✔" if idx.get("queryable", True) else "✖"
            L.append(f"| `{idx['ns']}` | `{idx['name']}` | {idx.get('type','?')} | {s_str} | {q} |")
    else:
        L.append("*No Search indexes found.*")
    L.append("")

    # Recommendations
    recs = [f["doc"] for f in crits + warns if f.get("doc")]
    if recs:
        L.append("## Recommendations\n")
        for r in recs:
            L.append(f"- {r}")
        L.append("")

    # Errors
    errors = (data or {}).get("global_errors") or []
    if errors:
        L += ["## ⚠ Errors Detected\n"] + [f"- `{e}`" for e in errors] + [""]

    L += ["---", "*Generated by [mongot-monitor](https://github.com/Miccolomi/mongot-monitor)*"]
    return "\n".join(L)


# ── JSON ──────────────────────────────────────────────────────────────────────

def build_json(data: dict, findings: list) -> dict:
    health, nc, nw, np_ = _health(findings)
    pods    = (data or {}).get("mongot_pods") or []
    prom_all= (data or {}).get("mongot_prometheus") or {}
    idxs    = (data or {}).get("search_indexes") or []
    oplog   = (data or {}).get("oplog_info") or {}

    return {
        "generated_at":   _ts(),
        "schema_version": "1",
        "health":         health.lower(),
        "pods": [
            {
                "name":           p["name"],
                "phase":          p.get("phase"),
                "all_ready":      p.get("all_ready"),
                "total_restarts": p.get("total_restarts", 0),
                "node":           p.get("node"),
                "namespace":      p.get("namespace"),
            }
            for p in pods
        ],
        "search_metrics": {
            pod_name: {
                "search_qps":             prom.get("categories", {}).get("search_commands", {}).get("search_qps", 0),
                "search_avg_latency_sec": prom.get("categories", {}).get("search_commands", {}).get("search_avg_latency_sec", 0),
                "vectorsearch_qps":       prom.get("categories", {}).get("search_commands", {}).get("vectorsearch_qps", 0),
                "indexing_lag_sec":       prom.get("categories", {}).get("indexing", {}).get("change_stream_lag_sec", 0),
                "initial_sync_active":    (prom.get("categories", {}).get("indexing", {}).get("initial_sync_in_progress") or 0) > 0,
            }
            for pod_name, prom in prom_all.items()
        },
        "oplog": {
            "window_hours": oplog.get("window_hours"),
            "head_time":    oplog.get("head_time"),
        },
        "advisor": {
            "health":   health.lower(),
            "summary":  {"crit": nc, "warn": nw, "pass": np_},
            "findings": [
                {
                    "status":         f.get("status"),
                    "title":          f.get("title"),
                    "detail":         f.get("value"),
                    "recommendation": f.get("doc"),
                }
                for f in findings
            ],
        },
        "search_indexes": [
            {
                "ns":        idx.get("ns"),
                "name":      idx.get("name"),
                "type":      idx.get("type"),
                "status":    idx.get("status"),
                "queryable": idx.get("queryable", True),
                "num_docs":  idx.get("num_docs"),
            }
            for idx in idxs
        ],
        "global_errors": (data or {}).get("global_errors") or [],
        "source":        "mongot-monitor",
    }
