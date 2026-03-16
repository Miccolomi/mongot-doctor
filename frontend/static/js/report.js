// ── Status Report Modal ───────────────────────────────────────────────────────

let _reportFmt = 'text';
let _reportContent = '';

function openReportModal() {
    const modal = document.getElementById('report-modal');
    modal.style.display = 'flex';
    _fetchReport('text');

    modal.addEventListener('click', function onBg(e) {
        if (e.target === modal) { closeReportModal(); modal.removeEventListener('click', onBg); }
    });
}

function closeReportModal() {
    document.getElementById('report-modal').style.display = 'none';
}

function switchFmt(fmt) {
    _reportFmt = fmt;
    ['text', 'markdown', 'json'].forEach(f => {
        const btn = document.getElementById(`fmt-${f}`);
        if (f === fmt) {
            btn.style.border = '1px solid #00b0ff';
            btn.style.background = '#00b0ff22';
            btn.style.color = '#00b0ff';
        } else {
            btn.style.border = '1px solid #1a1f2e';
            btn.style.background = 'transparent';
            btn.style.color = '#6b7394';
        }
    });
    _fetchReport(fmt);
}

async function _fetchReport(fmt) {
    const el = document.getElementById('report-content');
    el.textContent = '⏳ Generating report…';
    try {
        const r = await fetch(`/api/report?format=${fmt}`);
        if (fmt === 'json') {
            const data = await r.json();
            _reportContent = JSON.stringify(data, null, 2);
        } else {
            _reportContent = await r.text();
        }
        el.textContent = _reportContent;
    } catch(e) {
        el.textContent = `Error: ${e.message}`;
    }
}

function copyReport() {
    if (!_reportContent) return;
    navigator.clipboard.writeText(_reportContent).then(() => {
        const btn = document.querySelector('#report-modal button[onclick="copyReport()"]');
        const orig = btn.textContent;
        btn.textContent = '✔ Copied!';
        btn.style.color = '#00e676';
        setTimeout(() => { btn.textContent = orig; btn.style.color = '#00e676'; }, 2000);
    });
}

function downloadReport() {
    if (!_reportContent) return;
    const ext  = { text: 'txt', markdown: 'md', json: 'json' }[_reportFmt] || 'txt';
    const mime = _reportFmt === 'json' ? 'application/json' : 'text/plain';
    const ts   = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
    const blob = new Blob([_reportContent], { type: mime });
    const a    = document.createElement('a');
    a.href     = URL.createObjectURL(blob);
    a.download = `mongot-report-${ts}.${ext}`;
    a.click();
    URL.revokeObjectURL(a.href);
}

// Close on Escape
document.addEventListener('keydown', e => {
    if (e.key === 'Escape') closeReportModal();
});
