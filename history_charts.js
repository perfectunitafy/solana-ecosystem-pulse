/* Shared time-series charts from history.jsonl — pure SVG, zero deps.
   Renders into #hist-charts if present. Used by all dashboard variants. */
(function () {
  const host = document.getElementById('hist-charts');
  if (!host) return;
  const C = { tps: '#3fb950', tvl: '#58a6ff', price: '#d29922' };

  function svg(values, color, label, fmt) {
    const w = 1200, h = 110, padT = 18, padB = 14;
    const min = Math.min(...values), max = Math.max(...values), span = (max - min) || 1;
    const n = values.length;
    const pts = values.map((v, i) =>
      `${(10 + i * (w - 20) / Math.max(1, n - 1)).toFixed(1)},${(h - padB - (v - min) / span * (h - padT - padB)).toFixed(1)}`);
    const poly = pts.join(' ');
    const area = `10,${h - 2} ${poly} ${(10 + (n - 1) * (w - 20) / Math.max(1, n - 1)).toFixed(1)},${h - 2}`;
    return `<svg viewBox="0 0 ${w} ${h}" width="100%" height="${h}" preserveAspectRatio="none" style="display:block">
<polygon points="${area}" fill="${color}" opacity="0.12"/>
<line x1="0" y1="${h - padB - (0.5)}" x2="0" y2="0" stroke="none"/>
<polyline points="${poly}" fill="none" stroke="${color}" stroke-width="1.5"/>
<text x="8" y="13" fill="#8b949e" font-size="11" font-family="monospace">${label}</text>
<text x="8" y="${h - 4}" fill="#8b949e" font-size="10" font-family="monospace">min ${fmt(min)}</text>
<text x="${w - 8}" y="${h - 4}" fill="#8b949e" font-size="10" font-family="monospace" text-anchor="end">max ${fmt(max)} · now ${fmt(values[n - 1])}</text>
</svg>`;
  }

  function fmtN(v) {
    if (Math.abs(v) >= 1e9) return (v / 1e9).toFixed(2) + 'B';
    if (Math.abs(v) >= 1e6) return (v / 1e6).toFixed(2) + 'M';
    if (Math.abs(v) >= 1e3) return (v / 1e3).toFixed(1) + 'k';
    return v.toFixed(v < 100 ? 2 : 0);
  }

  function load() {
    const isAlt = window.location.pathname.includes('/alt/') || window.location.pathname.includes('/alt');
    const path = isAlt ? '../history.jsonl' : 'history.jsonl';
    fetch(path + '?t=' + Date.now())
      .then(r => r.text())
      .then(t => {
        const rows = t.trim() ? t.trim().split('\n').map(JSON.parse) : [];
        const seen = {};
        rows.forEach(r => seen[r.ts] = r);
        const pts = Object.values(seen).sort((a, b) => a.ts - b.ts);
        if (pts.length < 5) {
          host.innerHTML = '<p style="color:#8b949e;font-size:12px">accumulating history… (' + pts.length + ' samples)</p>';
          return;
        }
        const hrs = ((pts[pts.length - 1].ts - pts[0].ts) / 3600).toFixed(1);
        const cap = `<div style="color:#8b949e;font-size:11px;margin:2px 0 10px">${pts.length} samples · ${hrs}h window · snapshot per pipeline cycle</div>`;
        host.innerHTML =
          svg(pts.map(p => p.tps), C.tps, 'NETWORK TPS', fmtN) +
          svg(pts.map(p => p.tvl_usd), C.tvl, 'DeFi TVL (USD)', fmtN) +
          svg(pts.map(p => p.price_usd), C.price, 'SOL/USD', v => '$' + v.toFixed(2)) +
          cap;
      })
      .catch(() => {});
  }
  load();
  setInterval(load, 30000);
})();
