# Solana Ecosystem Pulse — Bounty Submission Draft

> **Bounty:** [Develop Solana Ecosystem Auto-Updating Report & Interactive Dashboard](https://superteam.fun/earn/listing/develop-solana-ecosystem-auto-updating-report-and-interactive-dashboard) — Superteam Canada, prize pool $1,000 USDG
>
> **Status:** DRAFT — finalize before submit (deadline Sep 1, 2026 03:59 UTC)

---

## Submission Text (for the Earn form)

**Solana Ecosystem Pulse** is a fully autonomous, zero-key telemetry pipeline that continuously monitors Solana network health, validator decentralization, market data, and DeFi TVL — and renders it as a live dark-theme dashboard with built-in anomaly detection.

### What's inside

- **Data layer:** public Solana JSON-RPC (3-endpoint failover: mainnet-beta / extrnode / ankr), OKX + DexScreener + CoinGecko price cascade, DeFiLlama historical TVL. **No private API keys anywhere.**
- **Analytics:** true TPS from `getRecentPerformanceSamples` (not inflated vote-TX counts), Nakamoto Coefficient computed live from stake distribution, delinquent-stake tracking, epoch progression with ETA.
- **Anomaly engine:** 5 threshold-based checks (TPS degradation, validator delinquency, stake centralization, SOL volatility, TVL migration) producing a weighted 0–100 Health Score.
- **Outputs:** interactive dashboard (3 UI styles), human-readable `report.md`, machine-readable `report.json` — exactly per bounty spec.
- **Automation:** pipeline loop every 15s; browser refreshes every 10s. History accumulates to JSONL for time-series charts.
- **Resilience:** multi-RPC failover, price-source cascade with live source badge, graceful degradation when any upstream fails.

### Links

- 🔴 **Live demo:** https://c86a8035373df0.lhr.life/dashboard.html
- 📦 **Source:** https://github.com/perfectunitafy/solana-ecosystem-pulse
- 📄 Sample reports: [/report.md](https://c86a8035373df0.lhr.life/report.md) · [/report.json](https://c86a8035373df0.lhr.life/report.json)
- 🎨 Alt UI styles: [TUI](https://c86a8035373df0.lhr.life/dashboard_v2.html) · [Terminal Amber](https://c86a8035373df0.lhr.life/dashboard_v3.html)

### Run it yourself

```bash
git clone https://github.com/perfectunitafy/solana-ecosystem-pulse && cd solana-ecosystem-pulse
python3 report_generator.py          # one full pipeline pass → report.json + report.md
python3 -m http.server 8080          # serve dashboard
# open http://localhost:8080/dashboard.html
```

Pure Python stdlib + vanilla JS. No dependencies. No build step.

---

## Pre-Submit Checklist

- [ ] Live demo URL responds 200 on all pages (dashboard, v2, v3, report.md, report.json)
- [ ] GitHub repo is public, README has current screenshots/description
- [ ] `history.jsonl` has accumulated meaningful data (>24h of samples) — mention in submission if yes
- [ ] Final read-through of submission text (word count ≤300 for the summary field)
- [ ] Wallet connected on Earn, profile page loads without client-side error
- [ ] Submit before deadline; screenshot confirmation

## Notes

- Tunnel URLs are ephemeral (localhost.run free tier). If the demo link dies before judging: regenerate tunnel and update links everywhere (`grep -rl "lhr.life" .`).
- Consider pinning key files via GitHub gist as backup evidence of history data.
