# Solana Ecosystem Pulse

Live, zero-key monitoring dashboard for the Solana Mainnet-Beta ecosystem: network performance, validator-set decentralization, token economics and DeFi TVL — aggregated every 15 seconds from public APIs only (no private API keys), with automated anomaly detection.

**Live demo:** https://fb165b4a4017c9.lhr.life/dashboard.html
*(tunnel URL may rotate; serve locally with `python3 -m http.server 8081`)*

## UI variants

| File | Style |
|---|---|
| `dashboard.html` | Grafana/GitHub-style dark dashboard (default) |
| `dashboard_v2.html` | Terminal style — monospace, thin rules, btop/k9s aesthetics |
| `dashboard_v3.html` | Financial terminal (Bloomberg-like) — amber on black, ticker tape, dense tables |

All variants read the same `report.json`, refresh every 10s and render accumulated TPS/TVL history charts from `history.jsonl`.

## Architecture

```
data_pipeline.py      → aggregates metrics from public sources
anomaly_detector.py   → rule-based anomaly engine + health score
report_generator.py   → writes report.json / report.md + appends history.jsonl snapshot
pipeline_loop.sh      → loop daemon, 15s interval
dashboard*.html       → dependency-free static dashboards (vanilla JS/Canvas)
```

### Data sources (all keyless)
- **Solana public JSON-RPC** (multi-endpoint failover): epoch info, recent performance samples (true TPS), vote accounts, supply, version
- **DeFiLlama**: Solana chain TVL, historical TVL, protocol breakdown
- **OKX → DexScreener → CoinGecko** cascade for SOL price/volume/market-cap

## Features
- True TPS computed from `getRecentPerformanceSamples` (not node-reported averages)
- Decentralization metrics: active/delinquent validators, stake concentration, **Nakamoto coefficient**
- Rule-based anomaly detection with severity levels and an ecosystem health score (0–100)
- Rolling 24h time-series (`history.jsonl`, one snapshot per pipeline cycle) rendered as lightweight Canvas charts
- Three complete UI themes, zero external dependencies, single static files

## Run

```bash
python3 report_generator.py        # one-shot pipeline run + reports
bash pipeline_loop.sh              # continuous mode (15s interval)
python3 -m http.server 8081        # serve dashboards at http://localhost:8081/dashboard.html
```

Requires Python 3.8+ (stdlib only).
