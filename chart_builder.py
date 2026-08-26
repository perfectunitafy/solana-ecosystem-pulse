#!/usr/bin/env python3
"""Builds charts.html — time-series SVG charts from history.jsonl, auto-served."""
import json, pathlib

BASE = pathlib.Path(__file__).parent

def sparkline_svg(values, w=600, h=90, color='#3fb950', label=''):
    vmin, vmax = min(values), max(values)
    if vmax - vmin < 1e-9:
        norm = [0.5] * len(values)
    else:
        norm = [(v - vmin) / (vmax - vmin) for v in values]
    n = len(norm)
    step_x = (w - 20) / max(1, n - 1)
    pts = [f"{10 + i*step_x:.1f},{h - 15 - p*(h-30):.1f}" for i, p in enumerate(norm)]
    poly = ' '.join(pts)
    area = f"10,{h-5} " + poly + f" {10+(n-1)*step_x:.1f},{h-5}"
    return f'''<svg viewBox="0 0 {w} {h}" width="100%" height="{h}" preserveAspectRatio="none">
<polygon points="{area}" fill="{color}" opacity="0.12"/>
<polyline points="{poly}" fill="none" stroke="{color}" stroke-width="1.6"/>
<text x="10" y="13" fill="#8b949e" font-size="10" font-family="sans-serif">{label}</text>
</svg>'''

def main():
    rows = [json.loads(l) for l in open(BASE / 'history.jsonl')]
    seen = {}
    for r in rows:
        seen[r['ts']] = r
    rows = sorted(seen.values(), key=lambda r: r['ts'])
    if len(rows) < 5:
        pathlib.Path(BASE / 'charts_snippet.html').write_text(
            '<!-- insufficient data: %d samples -->' % len(rows))
        return

    span_h = (rows[-1]['ts'] - rows[0]['ts']) / 3600
    tps = [r['tps'] for r in rows]
    price = [r['price_usd'] for r in rows]

    svg_tps = sparkline_svg(tps, color='#3fb950', label=f'NETWORK TPS · {len(rows)} samples · {span_h:.1f}h window')
    svg_price = sparkline_svg(price, color='#d29922', label='SOL/USD')

    html = f'''<!-- time-series section -->
<div style="max-width:1280px;margin:0 auto 12px;padding:0 20px">
<div class="panel col-12"><div class="panel-header">Network TPS — live history ({span_h:.1f}h)</div><div class="panel-body">{svg_tps}</div></div>
<div class="panel col-12" style="margin-top:12px"><div class="panel-header">SOL Price — live history</div><div class="panel-body">{svg_price}</div></div>
</div>'''

    out = BASE / 'charts_snippet.html'
    out.write_text(html)
    print(f"charts updated: {len(rows)} samples, {span_h:.1f}h span")

if __name__ == '__main__':
    main()
