# Superteam Canada Earn Submission — Solana Ecosystem Pulse

> **Draft — Влад: проверь ссылки и тон перед публикацией.**

## Title
Solana Ecosystem Pulse — Real-Time Zero-Key Network & DeFi Monitor

## What we built
A live monitoring dashboard for Solana Mainnet-Beta that aggregates network performance, validator-set decentralization, token economics and DeFi TVL every 15 seconds — using **only public, keyless APIs** (Solana public JSON-RPC with multi-endpoint failover, DeFiLlama, OKX/DexScreener/CoinGecko cascade). No private API keys, no paid tiers, nothing to configure.

On top of the raw data sits a rule-based anomaly-detection engine that flags network irregularities (TPS drops, delinquent-validator spikes, TVL shocks) and computes a 0–100 ecosystem health score.

## Live demo
- Default UI (Grafana-style): https://d5f3f47e8e06ee.lhr.life/dashboard.html
- Terminal UI (btop/k9s aesthetic): https://d5f3f47e8e06ee.lhr.life/dashboard_v2.html
- Financial-terminal UI (Bloomberg-like): https://d5f3f47e8e06ee.lhr.life/dashboard_v3.html

*(tunnel may rotate; all dashboards are static files — serve locally with `python3 -m http.server 8081`)*

## GitHub
https://github.com/<OWNER>/<REPO> *(← вставить актуальный URL)*

## Architecture
```
data_pipeline.py     → keyless aggregation (RPC failover, price-source cascade)
anomaly_detector.py  → rule engine + health score
report_generator.py  → report.json / report.md + rolling time-series (history.jsonl)
pipeline_loop.sh     → 15s loop daemon
dashboard*.html      → three dependency-free UI themes (vanilla JS + Canvas)
```

## Key features the jury should notice
1. **True TPS** computed from `getRecentPerformanceSamples`, not node-reported averages; min/avg/max over a 30-minute window.
2. **Decentralization metrics**: active/delinquent validators, delinquent stake %, total stake, **Nakamoto coefficient**, top-5 validators by stake.
3. **Anomaly detection** with severity levels and an explainable health score.
4. **Rolling 24h time-series**: one snapshot per pipeline cycle into `history.jsonl`, rendered as lightweight Canvas charts in all three UIs.
5. **Three complete UI designs** for the same data — zero external JS libraries, single static HTML files each.
6. **Zero configuration / zero keys** — clone and run with Python stdlib only.

## Stack
Python 3 (stdlib only) · vanilla HTML/CSS/JS · Canvas · bash. No frameworks, no build step.

## Roadmap (post-bounty)
- WebSocket subscription for sub-second updates
- Alert webhooks (Telegram/Discord)
- Jito MEV tips & priority-fee market metrics
