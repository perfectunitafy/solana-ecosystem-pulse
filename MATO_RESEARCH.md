# How People Actually Trade on Solana — A Data-Grounded Anatomy
### Research for Superteam Germany bounty · Draft v0.2 · Live data collected Aug 26 2026

> **Method note:** Every number below comes from public APIs queried on Aug 26, 2026: DexScreener (pair-level flow), DeFiLlama (TVL & DEX volumes), OKX/DexScreener/CoinGecko cross-verified prices, plus a continuously-running telemetry pipeline with 700+ network snapshots. Reproducible collection scripts: github.com/perfectunitafy/solana-ecosystem-pulse

---

## Executive Summary

Solana's trading activity is not one market. It is three stacked markets with different participants, different venues, and different physics:

1. **The custody layer** — $11.3B sitting in CEX hot wallets on-chain (Binance alone holds $6.6B). Most "users" never leave this layer to trade.
2. **The yield layer** — $4.45B in liquid staking, growing +27%/week. Capital parked for yield, not actively traded.
3. **The execution layer** — ~$2-3B/day across DEXes, dominated by three venues and, beneath them, by bots.

Understanding *how people actually trade* means understanding how capital moves between these layers — and why the loudest part of the market (DEX retail) is numerically the smallest.

---

## 1. The fuel: $15.9B of stablecoins

Trading requires dry powder. Solana hosts **$15.88B** in USD-pegged stablecoins (DeFiLlama, Aug 26). This is the ceiling of immediately-deployable buying power, and its weekly change is a better sentiment indicator than price itself.

## 2. Execution: where the transactions actually live

Top-15 Solana-native SOL pairs processed **$363M in 24h volume across ~974K transactions** (DexScreener):

| DEX | Pair | Volume 24h | Txns 24h | Buys/Sells |
|---|---|---|---|---|
| Orca | SOL/USDC | $193.9M | 97,367 | 49,305 / 48,062 |
| Meteora | SOL/USDC | $69.9M | 23,710 | 12,151 / 11,559 |
| Raydium CLMM | SOL/USDC | $16.9M | **254,171** | 139,342 / 114,829 |
| Raydium | SOL/USDT | $7.0M | 107,523 | 57,403 / 50,120 |

Three structural facts hide in this table:

**(a) Volume ≠ activity.** Orca's flagship pool does 11× the volume of Raydium CLMM's busiest pool but has 2.6× *fewer* transactions. Average trade size on Orca: ~$2,000. On Raydium CLMM: ~$64. Two different species of trader inhabit nominally identical SOL/USDC pools.

**(b) Buy/sell parity is machine-perfect.** Every major pool sits within ±3% of a 50/50 buy-sell split. Humans in a directional mood break parity; bots enforcing arbitrage restore it within seconds. Flow data at this level measures bot infrastructure density, not human conviction.

**(c) The aggregator is the real venue.** Routing a 10,000 SOL (~$1M) sell through Jupiter splits it across 4 hops through pools whose names change entirely at each size tier (live sampling: Quantum → Aquifer → Scorch → TesseraV). A human choosing "Orca vs Raydium" is answering last decade's question; routers fragment every order optimally, and total price impact on $1M was 0.066%.

## 3. The yield layer: where idle capital goes

$4.45B in liquid staking (Sanctum $1.47B, Jito $0.97B, Binance staked SOL $1.0B), growing +25–28% week-over-week across all major providers. Compare DEX TVL growth (+25%) — they're moving together, suggesting the same capital rotation drives both: holders want yield on everything, everywhere, always.

This changes what "trading" means for most of the market: the default action isn't swapping tokens, it's **rebalancing between yield configurations**. LST positions are the new cash; swaps are the exception.

## 4. The custody layer: Binance is Solana's biggest DeFi protocol

On-chain CEX reserves total **$11.3B** — more than lending ($2.24B) and DEXes ($2.05B) combined. Binance's wallets alone hold $6.59B (+25%/week).

Translation: the largest single concentration of tradable Solana capital belongs to an off-chain order book. When the market moves, most of the selling never touches a Solana DEX. On-chain flow analysis that ignores CEX wallets reads maybe a third of the actual market.

## 5. What our own telemetry adds: coherence and churn

Running a continuous pipeline (500+ snapshots over multiple days):
- **Cross-venue spread** (OKX vs on-chain DEXes): consistently 0.08–0.15%. Arbitrage keeps CEX and DEX prices locked to sub-basis-point precision — venue selection is not a price decision anymore.
- **Validator churn**: single-validator activations/deactivations happen multiple times per hour around a stable baseline (~684 active). The validator set is fluid; consensus is not fragile.
- **Network TPS** averaged ~3,300 (range 2,931–3,790). Top-15 SOL pair trading alone accounts for roughly 11 TPS sustained — under half a percent of throughput. Trading is economically dominant but physically tiny on Solana.

---

## Practical takeaways

**If you're choosing where to execute:** your router already optimizes better than you can. Choose on MEV protection and UX, not headline TVL.

**If you're building a trading product:** your real competition for user attention is a liquid-staking UI offering passive yield, not another DEX.

**If you're analyzing the market:** stop counting wallets. Start segmenting flows by source (CEX inflow vs native), size (retail CLMM dust vs Orca blocks), and cohort behavior. Wallet counts are noise; user-source attribution is signal.

---

*Data sources & reproducibility: DexScreener API (pair flows), DeFiLlama (TVL/stablecoins/DEX volumes), OKX + CoinGecko (price verification), own pipeline (github.com/perfectunitafy/solana-ecosystem-pulse). All queries Aug 26, 2026.*

---

## TODO before submission (Aug 31)
- [ ] Add 5-day history.jsonl time-series chart (own data — unique among submissions)
- [ ] Verify current numbers still accurate or update
- [ ] Format per bounty deliverable requirements
- [ ] Submit via earn.superteam.fun
