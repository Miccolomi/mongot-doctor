"""
Search Index Inspector
Fetches full Search index definitions via $listSearchIndexes and produces
per-index observations (warn/crit/info) about mapping quality and health.
"""

import logging

log = logging.getLogger("mongot-monitor.index_inspector")

# ── Helpers ───────────────────────────────────────────────────────────────────

def _count_fields(fields_dict: dict) -> int:
    """Recursively count explicitly mapped fields (fullText index)."""
    if not isinstance(fields_dict, dict):
        return 0
    total = 0
    for v in fields_dict.values():
        total += 1
        if isinstance(v, dict) and "fields" in v:
            total += _count_fields(v["fields"])
    return total


def _analyze_fulltext(idx_def: dict) -> tuple[bool, int]:
    """Return (is_dynamic, field_count) for a fullText index."""
    mappings = idx_def.get("mappings", {})
    is_dynamic = bool(mappings.get("dynamic", False))
    field_count = _count_fields(mappings.get("fields", {}))
    return is_dynamic, field_count


def _analyze_vector(idx_def: dict) -> int:
    """Return number of vector fields configured."""
    return len(idx_def.get("fields", []))


# ── Core ──────────────────────────────────────────────────────────────────────

def inspect_search_indexes(mongo_client) -> list[dict]:
    """
    Iterate all non-system databases/collections, fetch Search index definitions,
    run analysis checks, return a list of index reports.

    Each report:
    {
        "ns":             "db.collection",
        "name":           "default",
        "type":           "fullText" | "vectorSearch",
        "status":         "READY" | "BUILDING" | "FAILED" | ...,
        "queryable":      bool,
        "num_docs":       int | None,
        "mapping_dynamic": bool | None,    # fullText only
        "field_count":    int,             # fullText: explicit fields; vector: vector fields
        "observations":   [{"level": "warn"|"crit"|"info", "msg": str, "suggestion": str}]
    }
    """
    if not mongo_client:
        return []

    results = []

    try:
        db_names = [d for d in mongo_client.list_database_names()
                    if d not in ("admin", "local", "config")]
    except Exception as e:
        log.warning(f"Cannot list databases: {e}")
        return []

    # Track indexes per collection to detect over-indexing
    ns_index_count: dict[str, int] = {}

    for db_name in db_names:
        db = mongo_client[db_name]
        try:
            coll_names = db.list_collection_names()
        except Exception:
            continue

        for coll_name in coll_names:
            ns = f"{db_name}.{coll_name}"
            raw_indexes = []

            try:
                raw_indexes = list(db[coll_name].aggregate([{"$listSearchIndexes": {}}]))
            except Exception:
                try:
                    raw_indexes = list(db[coll_name].list_search_indexes())
                except Exception:
                    pass

            if not raw_indexes:
                continue

            ns_index_count[ns] = len(raw_indexes)

            for idx in raw_indexes:
                idx_name   = idx.get("name", "default")
                idx_type   = "vectorSearch" if idx.get("type") == "vectorSearch" else "fullText"
                status     = idx.get("status", "READY")
                queryable  = idx.get("queryable", True)
                definition = idx.get("latestDefinition", idx.get("definition", {}))

                # Mapping analysis
                mapping_dynamic = None
                field_count = 0
                if idx_type == "fullText":
                    mapping_dynamic, field_count = _analyze_fulltext(definition)
                elif idx_type == "vectorSearch":
                    field_count = _analyze_vector(definition)

                # Doc count (best-effort)
                num_docs = None
                try:
                    num_docs = db[coll_name].estimated_document_count()
                except Exception:
                    pass

                observations = _build_observations(
                    status, queryable, idx_type,
                    mapping_dynamic, field_count
                )

                results.append({
                    "ns":              ns,
                    "name":            idx_name,
                    "type":            idx_type,
                    "status":          status,
                    "queryable":       queryable,
                    "num_docs":        num_docs,
                    "mapping_dynamic": mapping_dynamic,
                    "field_count":     field_count,
                    "observations":    observations,
                })

    # Post-pass: flag collections with too many indexes
    for report in results:
        if ns_index_count.get(report["ns"], 0) > 3:
            report["observations"].append({
                "level":      "warn",
                "msg":        f"Collection has {ns_index_count[report['ns']]} Search indexes",
                "suggestion": "Multiple indexes increase indexing overhead — consolidate if possible",
            })

    return results


def _build_observations(status, queryable, idx_type, mapping_dynamic, field_count) -> list[dict]:
    obs = []

    if status == "FAILED":
        obs.append({
            "level":      "crit",
            "msg":        "Index is in FAILED state",
            "suggestion": "Check mongot logs for indexing errors and recreate the index",
        })

    if not queryable:
        obs.append({
            "level":      "crit",
            "msg":        "Index is not queryable",
            "suggestion": "Verify mongot is running and connected to mongod, then check index status",
        })

    if status == "BUILDING":
        obs.append({
            "level":      "warn",
            "msg":        "Index is still building",
            "suggestion": "Wait for READY state before running Search queries against this index",
        })

    if idx_type == "fullText":
        if mapping_dynamic:
            obs.append({
                "level":      "warn",
                "msg":        "Dynamic mapping enabled — every document field is indexed",
                "suggestion": "Restrict mapping to specific fields to reduce index size and improve performance",
            })

        if not mapping_dynamic and field_count == 0:
            obs.append({
                "level":      "warn",
                "msg":        "No fields mapped and dynamic is disabled",
                "suggestion": "Index will return no results — add explicit field mappings or enable dynamic",
            })

        if field_count > 20:
            obs.append({
                "level":      "warn",
                "msg":        f"Large explicit mapping ({field_count} fields)",
                "suggestion": "Review mapping and remove fields not used in active Search queries",
            })

    return obs


# ── Summary ───────────────────────────────────────────────────────────────────

def summarize(reports: list[dict]) -> dict:
    crits  = sum(1 for r in reports for o in r["observations"] if o["level"] == "crit")
    warns  = sum(1 for r in reports for o in r["observations"] if o["level"] == "warn")
    clean  = sum(1 for r in reports if not r["observations"])
    return {
        "total_indexes": len(reports),
        "clean":  clean,
        "warns":  warns,
        "crits":  crits,
        "health": "critical" if crits else "degraded" if warns else "healthy",
    }
