#!/usr/bin/env python3
"""
Solana Ecosystem Pulse — Multi-format Report Generator
Generates: report.json (machine), report.md (human-readable).
"""

import json
import time
from pathlib import Path
from typing import Dict, Any

from data_pipeline import SolanaDataPipeline, append_history_snapshot
from anomaly_detector import AnomalyDetector
from price_spread import fetch_all as fetch_spread_prices, analyze as analyze_spread
import trend_analyzer

BASE = Path(__file__).parent


def fmt_usd(v: float) -> str:
    if v >= 1e9:
        return f"${v/1e9:.2f}B"
    if v >= 1e6:
        return f"${v/1e6:.2f}M"
    return f"${v:,.2f}"


def generate_markdown(d: Dict[str, Any], anomalies: Dict[str, Any]) -> str:
    net, val, eco, defi = d["network_performance"], d["validators"], d["economics"], d["defi"]
    meta = d["meta"]

    status_icon = {"HEALTHY": "🟢", "WARNING": "🟡", "CRITICAL": "🔴"}.get(anomalies["overall_status"], "⚪")

    md = []
    md.append(f"# 🌐 Solana Ecosystem Pulse Report")
    md.append(f"> **Generated:** {meta['generated_at_utc']} · **Pipeline:** v{meta['pipeline_version']} · {status_icon} Status: **{anomalies['overall_status']}** (Health: {anomalies['ecosystem_health_score']}/100)\n")

    # Anomalies section first (most important)
    md.append(f"## ⚠ Anomaly Detection ({anomalies['anomaly_count']})\n")
    if not anomalies["anomalies"]:
        md.append("✅ No anomalies detected. All network telemetry within optimal parameters.\n")
    else:
        for a in anomalies["anomalies"]:
            icon = "🔴" if a["severity"] == "CRITICAL" else "🟡"
            md.append(f"- {icon} **{a['metric']}** — `{a['value']}`\n  - {a['description']}")
        md.append("")

    md.append("## ⚡ Network Performance\n")
    md.append("| Metric | Value |")
    md.append("|---|---|")
    md.append(f"| Current TPS | **{net['current_tps']:,}** |")
    md.append(f"| Avg TPS (30m window) | {net['avg_tps_30m']:,} |")
    md.append(f"| TPS Range (30m) | {net['min_tps_30m']:,} – {net['max_tps_30m']:,} |")
    md.append(f"| Epoch | #{net['epoch']} ({net['epoch_progress_pct']}% complete) |")
    md.append(f"| Est. epoch end | ~{net['est_hours_remaining']}h remaining |")
    md.append(f"| Absolute Slot | {net['absolute_slot']:,} |")
    md.append(f"| Block Height | {net['block_height']:,} |")
    md.append(f"| solana-core version | {net['solana_core_version']} |\n")

    md.append("## 🔐 Validator Set & Decentralization\n")
    md.append("| Metric | Value |")
    md.append("|---|---|")
    md.append(f"| Active Validators | **{val['active_validators']}** |")
    md.append(f"| Delinquent Validators | {val['delinquent_validators']} ({val['delinquent_stake_pct']}% of stake) |")
    md.append(f"| Total Active Stake | {val['total_active_stake_sol']:,.0f} SOL |")
    md.append(f"| **Nakamoto Coefficient** | **{val['nakamoto_coefficient']}** (min nodes to halt consensus) |\n")

    md.append("### Top 5 Validators by Active Stake\n")
    md.append("| Rank | Vote Pubkey | Stake (SOL) | % | Commission |")
    md.append("|---|---|---|---|---|")
    for i, v in enumerate(val["top_5_validators"], 1):
        md.append(f"| {i} | `{v['vote_pubkey']}` | {v['stake_sol']:,.0f} | {v['stake_pct']}% | {v['commission_pct']}% |")
    md.append("")

    md.append("## 💰 Token Economics\n")
    md.append("| Metric | Value |")
    md.append("|---|---|")
    md.append(f"| SOL Price | **${eco['price_usd']:,}** ({eco['change_24h_pct']:+.2f}% / 24h) |")
    md.append(f"| Market Cap | {fmt_usd(eco['market_cap_usd'])} |")
    md.append(f"| 24h Volume | {fmt_usd(eco['volume_24h_usd'])} |")
    md.append(f"| Circulating Supply | {eco['circulating_sol']:,.0f} SOL |")
    md.append(f"| Total Supply | {eco['total_supply_sol']:,.0f} SOL |\n")

    md.append("## 🏦 DeFi & TVL\n")
    md.append("| Metric | Value |")
    md.append("|---|---|")
    md.append(f"| Solana Chain TVL | **{fmt_usd(defi['tvl_usd'])}** ({defi['tvl_change_24h_pct']:+.2f}% / 24h, {defi.get('tvl_change_7d_pct', 0):+.2f}% / 7d) |\n")
    
    if defi.get("top_protocols"):
        md.append("### Top Protocols on Solana (by TVL)\n")
        md.append("| Protocol | Category | TVL | 24h Δ |")
        md.append("|---|---|---|---|")
        for p in defi["top_protocols"]:
            md.append(f"| {p['name']} | {p['category']} | {fmt_usd(p['tvl_solana_usd'])} | {p['change_1d']:+.2f}% |")
        md.append("")

    md.append("---\n")
    md.append("*Automated pipeline: Solana JSON-RPC + CoinGecko/Binance + DeFiLlama. Zero private API keys required.*")
    md.append("")
    return "\n".join(md)


def main():
    print("[1/4] Aggregating on-chain + off-chain data...")
    pipeline = SolanaDataPipeline()
    data = pipeline.run_full_aggregation()

    print("[2/4] Running anomaly detection engine...")
    detector = AnomalyDetector()
    anomalies = detector.analyze(data)

    print("[2.5/4] Cross-source price verification (arbitrage spread)...")
    try:
        spread = analyze_spread(fetch_spread_prices())
        data["price_verification"] = spread
        if "error" not in spread:
            data["economics"]["price_source"] += f" | cross-check: {spread['verdict']} ({spread['spread_pct']}% across {spread['sources_up']} sources)"
    except Exception:
        data["price_verification"] = {"error": "spread check failed"}

    print("[2.7/4] Trend analysis over history...")
    try:
        data["trends"] = trend_analyzer.analyze()
    except Exception:
        data["trends"] = {"error": "insufficient history"}

    combined = dict(data)
    combined["anomalies"] = anomalies

    combined_for_history = dict(data)
    combined_for_history["anomalies"] = anomalies
    append_history_snapshot(combined_for_history)  # snapshot with health score

    print("[3/4] Writing machine-readable JSON...")
    json_path = BASE / "report.json"
    json_path.write_text(json.dumps(combined, indent=2, ensure_ascii=False))

    print("[4/4] Writing human-readable Markdown...")
    md_path = BASE / "report.md"
    md_path.write_text(generate_markdown(data, anomalies))

    print(f"\n✓ Reports generated:")
    print(f"  → {json_path} ({json_path.stat().st_size:,} bytes)")
    print(f"  → {md_path} ({md_path.stat().st_size:,} bytes)")
    print(f"\nStatus: {anomalies['overall_status']} | Health Score: {anomalies['ecosystem_health_score']}/100")


if __name__ == "__main__":
    main()
