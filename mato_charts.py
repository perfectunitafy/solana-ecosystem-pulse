#!/usr/bin/env python3
"""Publication-grade charts for Mato research from own telemetry history."""
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timezone

rows = [json.loads(l) for l in open('/home/administrator/solpulse-dashboard/history.jsonl')]
seen = {r['ts']: r for r in rows}
rows = sorted(seen.values(), key=lambda r: r['ts'])

times = [datetime.fromtimestamp(r['ts'], tz=timezone.utc) for r in rows]
tps = [r['tps'] for r in rows]
price = [r['price_usd'] for r in rows]
tvl = [r['tvl_usd'] for r in rows]

plt.rcParams.update({
    'figure.facecolor': 'white', 'axes.facecolor': '#fafafa',
    'axes.edgecolor': '#cccccc', 'axes.grid': True, 'grid.color': '#e5e5e5',
    'font.size': 10, 'axes.titlesize': 12, 'axes.titleweight': 'bold'
})

fig, axes = plt.subplots(3, 1, figsize=(11, 9), sharex=True)
fig.suptitle(f'Solana Network Telemetry — {len(rows)} snapshots over {(times[-1]-times[0]).total_seconds()/3600:.1f}h (live pipeline)',
             fontsize=13, fontweight='bold', y=0.98)

ax = axes[0]
ax.plot(times, tps, color='#3fb950', linewidth=1.2)
ax.fill_between(times, min(tps), tps, alpha=0.15, color='#3fb950')
avg = sum(tps)/len(tps)
ax.axhline(avg, color='#8b949e', linestyle='--', linewidth=0.8, label=f'avg {avg:,.0f}')
ax.set_ylabel('TPS')
ax.set_title('Network Throughput (true TPS from performance samples)')
ax.legend(loc='upper right', fontsize=9)

ax = axes[1]
ax.plot(times, price, color='#d29922', linewidth=1.2)
ax.set_ylabel('SOL/USD')
ax.set_title('SOL Price (cross-verified: OKX primary)')
pmin, pmax = min(price), max(price)
ax.set_ylim(pmin - (pmax-pmin)*0.15, pmax + (pmax-pmin)*0.15)

ax = axes[2]
tvl_base = tvl[0]
ax.plot(times, [(t-tvl_base)/tvl_base*100 for t in tvl], color='#58a6ff', linewidth=1.2)
ax.axhline(0, color='#8b949e', linestyle='--', linewidth=0.8)
ax.set_ylabel('TVL Δ from window start (%)')
ax.set_title('Solana DeFi TVL — % change over observation window')
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
ax.set_xlabel('UTC time')

for ax in axes:
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig('/home/administrator/solpulse-dashboard/docs/mato_telemetry_chart.png', dpi=150, bbox_inches='tight')
print("chart saved: docs/mato_telemetry_chart.png")
print(f"data: {len(rows)} pts, {times[0]:%H:%M}–{times[-1]:%H:%M} UTC")
