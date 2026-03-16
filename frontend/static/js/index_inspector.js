// ── Search Index Inspector Panel ─────────────────────────────────────────────

let _indexInspectorInit = false;

function setupIndexInspector() {
    if (_indexInspectorInit) return;
    _indexInspectorInit = true;

    const banner = document.getElementById('index-inspector-banner');
    if (!banner) return;

    banner.innerHTML = `<div id="ii-results"></div>`;
    runIndexInspector();
}

async function runIndexInspector() {
    const results = document.getElementById('ii-results');
    if (!results) return;

    results.innerHTML = `<div style="background:#0a0d14;border:1px solid #1a1f2e;border-radius:10px;padding:14px;margin-bottom:10px;font-size:11px;color:#6b7394">
      ⏳ Inspecting Search indexes…</div>`;

    try {
        const r    = await fetch('/api/indexes/inspect');
        const data = await r.json();
        results.innerHTML = buildIndexInspectorHTML(data);
    } catch (e) {
        results.innerHTML = `<div style="color:#ff6b6b;font-size:11px;padding:8px">Index Inspector error: ${escapeHtml(e.message)}</div>`;
    }
}

function buildIndexInspectorHTML(data) {
    if (data.error) {
        if (data.error.includes('not configured')) {
            return `<div style="background:#0a0d1488;border:1px solid #1a1f2e;border-radius:10px;padding:14px;margin-bottom:10px;font-size:11px;color:#6b7394">
              🔍 <b>Search Index Inspector</b> — MongoDB not connected. Pass <code>--uri</code> to enable.
            </div>`;
        }
        return `<div style="background:#ff174411;border:1px solid #ff174444;border-radius:10px;padding:12px;margin-bottom:10px;font-size:11px;color:#ff6b6b">
          ✖ Index Inspector error: ${escapeHtml(data.error)}
        </div>`;
    }

    const s       = data.summary || {};
    const indexes = data.indexes || [];

    if (!indexes.length) {
        return `<div style="background:#0a0d14;border:1px solid #1a1f2e;border-radius:10px;padding:16px;margin-bottom:10px;font-size:12px;color:#6b7394">
          No Search indexes found in this cluster.
        </div>`;
    }

    const healthColor = s.health === 'critical' ? '#ff1744' : s.health === 'degraded' ? '#ffab00' : '#00e676';
    const healthIcon  = s.health === 'critical' ? '🔴' : s.health === 'degraded' ? '🟡' : '🟢';

    let h = `<div style="background:#0a0d14;border:1px solid #1a1f2e;border-radius:10px;padding:20px;margin-bottom:10px;">`;

    // Header row
    h += `<div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px;margin-bottom:18px">
      <div>
        <div style="font-size:15px;font-weight:700;color:${healthColor}">${healthIcon} ${s.total_indexes} index(es) — ${(s.health || 'healthy').toUpperCase()}</div>
      </div>
      <div style="display:flex;align-items:center;gap:16px;flex-wrap:wrap">
        <div style="display:flex;gap:16px;font-size:12px;font-weight:600">
          <span style="color:#ff1744">✖ ${s.crits} critical</span>
          <span style="color:#ffab00">⚠ ${s.warns} warnings</span>
          <span style="color:#00e676">✔ ${s.clean} clean</span>
        </div>
        <button onclick="runIndexInspector()" class="btn" style="padding:5px 14px;font-size:11px;font-weight:700;background:#1a2a4a;color:#00b0ff;border:1px solid #00b0ff44;border-radius:6px;">
          ↺ Refresh
        </button>
      </div>
    </div>`;

    // Index cards grid
    h += `<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:12px">`;

    indexes.forEach(idx => {
        const hasCrit = idx.observations.some(o => o.level === 'crit');
        const hasWarn = idx.observations.some(o => o.level === 'warn');
        const borderColor = hasCrit ? '#ff1744' : hasWarn ? '#ffab00' : '#00e676';
        const statusColor = idx.status === 'FAILED' ? '#ff1744' : idx.status === 'BUILDING' ? '#ffab00' : '#00e676';

        let mappingLine = '';
        if (idx.type === 'fullText') {
            mappingLine = idx.mapping_dynamic
                ? `<span style="color:#ffab00">dynamic ⚠</span>`
                : `<span style="color:#c9d1e0">static — ${idx.field_count} fields</span>`;
        } else {
            mappingLine = `<span style="color:#b388ff">${idx.field_count} vector field(s)</span>`;
        }

        const docsLabel = idx.num_docs != null ? idx.num_docs.toLocaleString() + ' docs' : '—';

        h += `<div style="background:#080b12;border:1px solid ${borderColor}44;border-left:3px solid ${borderColor};border-radius:8px;padding:12px">`;
        h += `<div style="font-size:10px;font-weight:700;color:#6b7394;margin-bottom:2px;font-family:monospace">${escapeHtml(idx.ns)}</div>`;
        h += `<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
          <span style="font-size:12px;font-weight:700;color:#c9d1e0">${escapeHtml(idx.name)}</span>
          <span style="font-size:10px;background:${statusColor}22;color:${statusColor};border:1px solid ${statusColor}44;border-radius:4px;padding:1px 7px;font-weight:700">${escapeHtml(idx.status)}</span>
        </div>`;
        h += `<div style="font-size:10px;color:#6b7394;margin-bottom:6px">${escapeHtml(idx.type)} &bull; ${docsLabel} &bull; Mapping: ${mappingLine}</div>`;

        if (!idx.observations.length) {
            h += `<div style="font-size:10px;color:#00e676">✔ No issues detected</div>`;
        } else {
            idx.observations.forEach(o => {
                const oc = o.level === 'crit' ? '#ff1744' : '#ffab00';
                const oi = o.level === 'crit' ? '✖' : '⚠';
                h += `<div style="margin-top:6px">
                  <div style="font-size:10px;font-weight:700;color:${oc}">${oi} ${escapeHtml(o.msg)}</div>
                  <div style="font-size:9px;color:#c9d1e0;padding-left:12px;margin-top:2px;line-height:1.5">→ ${escapeHtml(o.suggestion)}</div>
                </div>`;
            });
        }

        h += `</div>`;
    });

    h += `</div></div>`;
    return h;
}
