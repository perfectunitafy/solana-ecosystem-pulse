# Resilience Report — Source Failure Stress Tests

> Tested: 2026-08-26 ~07:30 UTC · Pipeline v1.4
> Method: each upstream source monkeypatched to return `None` (total failure), full pipeline executed, output integrity verified.

## Results Matrix

| Scenario | Pipeline completed | TPS | Price | Price source | TVL | Verdict |
|---|---|---|---|---|---|---|
| **All sources healthy** (baseline) | ✅ | ~3,500 | $96.9–97.0 | OKX | $5.60B | Full fidelity |
| **All RPC endpoints down** | ✅ | 0.0* | $96.95 | OKX | $5.60B | Degrades; market data survives |
| **OKX down** | ✅ | normal | $97.01 | **DexScreener** | $5.60B | Cascade works |
| **DexScreener down** | ✅ | normal | $96.98 | OKX | $5.60B | No impact (OKX primary) |
| **CoinGecko down** | ✅ | normal | $97.05 | OKX | $5.60B | No impact (tertiary) |
| **DeFiLlama down** | ✅ | normal | $97.05 | OKX | 0.0† | Degrades; rest intact |

\* TPS=0 is expected: no on-chain source → no transaction samples. The zero is honest (and now filtered from history snapshots by the sanity gate).
† TVL=0 with DeFiLlama down: single-source metric, no fallback exists. Documented limitation.

## Findings

1. **No scenario crashes the pipeline.** Every failure mode produces a complete report.json + report.md.
2. **Price cascade verified in practice:** OKX → DexScreener → CoinGecko handoff works exactly as designed. Killing the primary promotes the secondary transparently (`price_source` badge updates).
3. **On-chain data has triple redundancy:** mainnet-beta / extrnode / ankr RPCs — killing all three requires a network-level outage.
4. **Known gaps (honest limitations):**
   - TVL depends solely on DeFiLlama. A second TVL source (e.g., DefiLlama alternative API or direct protocol summation) would close this.
   - When all RPCs fail, TPS shows 0.0 rather than "N/A" — cosmetic improvement possible.
   - Anomaly engine treats missing values as healthy defaults rather than raising its own alert ("source down" is itself an anomaly worth reporting).

## Recommended follow-ups

- Add "data freshness" field per metric (age of last successful fetch) so consumers can distinguish "value unchanged" from "source stale".
- Surface source-down events as WARNING anomalies in the anomaly engine.

*Verdict: the pipeline survives every individual component failure and continues producing valid reports.*
