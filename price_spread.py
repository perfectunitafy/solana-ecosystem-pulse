#!/usr/bin/env python3
"""Cross-source SOL price verification: OKX vs DexScreener vs CoinGecko.
Outputs spread metrics into report.json (arbitrage intelligence)."""
import json, urllib.request, time

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Pulse/1.0"})
    try:
        return json.loads(urllib.request.urlopen(req, timeout=10).read())
    except Exception:
        return None

def fetch_all():
    prices = {}
    okx = get("https://www.okx.com/api/v5/market/ticker?instId=SOL-USDT")
    if okx and okx.get("data"):
        prices["okx"] = float(okx["data"][0]["last"])
    dx = get("https://api.dexscreener.com/latest/dex/tokens/So11111111111111111111111111111111111111112")
    if dx:
        pairs = [p for p in dx.get("pairs", []) if p.get("quoteToken", {}).get("symbol") in ("USDC", "USDT")]
        if pairs:
            best = max(pairs, key=lambda x: (x.get("liquidity") or {}).get("usd") or 0)
            prices["dexscreener"] = float(best.get("priceUsd") or 0)
    cg = get("https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd")
    if cg and "solana" in cg:
        prices["coingecko"] = float(cg["solana"]["usd"])
    return prices

def analyze(prices):
    if len(prices) < 2:
        return {"error": "insufficient sources", "sources_up": list(prices.keys())}
    vals = list(prices.values())
    vmin, vmax = min(vals), max(vals)
    spread_abs = round(vmax - vmin, 3)
    spread_pct = round((vmax - vmin) / vmin * 100, 4)
    avg = round(sum(vals) / len(vals), 3)
    # outlier detection: any source deviating >0.15% from median
    srt = sorted(vals); mid = srt[len(srt)//2]
    outliers = [k for k, v in prices.items() if abs(v - mid) / mid > 0.0015]
    return {
        "timestamp": int(time.time()),
        "prices": {k: round(v, 3) for k, v in prices.items()},
        "spread_abs_usd": spread_abs,
        "spread_pct": spread_pct,
        "avg_price": avg,
        "outlier_sources": outliers,
        "sources_up": len(prices),
        "verdict": "COHERENT" if spread_pct < 0.1 else ("MINOR_DRIFT" if spread_pct < 0.35 else "DIVERGENCE")
    }

if __name__ == "__main__":
    result = analyze(fetch_all())
    print(json.dumps(result, indent=2))
