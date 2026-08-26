# Solana Ecosystem Pulse — Endpoint Reference

All endpoints are free public tiers. No authentication required.

## Solana JSON-RPC

Base URLs (failover order):
1. `https://api.mainnet-beta.solana.com`
2. `https://solana-mainnet.rpc.extrnode.com`
3. `https://rpc.ankr.com/solana`

Request: POST, `Content-Type: application/json`, body:
```json
{"jsonrpc":"2.0","id":1,"method":"<method>","params":[<params>]}
```

| Method | Params | Key response fields |
|---|---|---|
| getEpochInfo | — | epoch, slotIndex, slotsInEpoch, absoluteSlot, blockHeight |
| getRecentPerformanceSamples | [N] | numTransactions, samplePeriodSecs → TPS = numTx/sec |
| getVoteAccounts | — | current[], delinquent[] with votePubkey, activatedStake, commission |
| getSupply | [{"excludeNonCirculatingAccountsList":true}] | value.total, value.circulating (lamports ÷ 1e9 = SOL) |
| getVersion | — | solana-core string |
| getHealth | — | "ok" status check |

## Price Sources (cascade order)

### 1. OKX (primary — includes 24h open for delta)
GET https://www.okx.com/api/v5/market/ticker?instId=SOL-USDT
→ data[0].last, data[0].open24h, data[0].volCcy24h

### 2. DexScreener (secondary)
GET https://api.dexscreener.com/latest/dex/tokens/So11111111111111111111111111111111111111112
→ pairs[] filter chainId=="solana"; best by liquidity.usd; priceUsd, volume.h24, priceChange.h24

### 3. CoinGecko (tertiary — rate-limited)
GET https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd
→ solana.usd

## DeFi TVL

Historical chain TVL: GET https://api.llama.fi/v2/historicalChainTvl/Solana
→ [{date: unix_sec, tvl: usd}, ...]

Protocol breakdown: GET https://api.llama.fi/protocols
→ filter chainTvls.Solana > threshold; sort desc

## Spread Verdict Thresholds

- COHERENT: < 0.10%
- MINOR_DRIFT: < 0.35%
- DIVERGENCE: ≥ 0.35%
- Outlier: > 0.15% deviation from median

## Anomaly Thresholds

| Check | WARNING | CRITICAL |
|---|---|---|
| TPS | < 2,000 | < 1,000 |
| Delinquent stake % | > 1.5% | > 5% |
| Nakamoto Coefficient | < 15 | < 10 |
| SOL 24h Δ | > ±7.5% | — |
| TVL 24h Δ | > ±5% | — |

Health Score: start at 100; −30 per CRITICAL, −10 per WARNING; clamp [0,100].
