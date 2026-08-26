#!/usr/bin/env python3
"""Trend analysis over history.jsonl: SMA(1h/6h), direction detection, validator churn."""
import json, pathlib

BASE = pathlib.Path(__file__).parent

def load_history():
    p = BASE / "history.jsonl"
    if not p.exists():
        return []
    rows = [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
    seen = {}
    for r in rows:
        seen[r["ts"]] = r
    return sorted(seen.values(), key=lambda r: r["ts"])

def sma(values, window_n):
    if len(values) < window_n:
        return round(sum(values) / len(values), 1)
    return round(sum(values[-window_n:]) / window_n, 1)

def direction(values):
    if len(values) < 10:
        return "INSUFFICIENT_DATA"
    half = len(values) // 2
    first, second = sum(values[:half]) / half, sum(values[half:]) / half
    delta = (second - first) / first * 100
    if delta > 1.5:
        return f"RISING ({delta:+.1f}%)"
    if delta < -1.5:
        return f"FALLING ({delta:+.1f}%)"
    return f"STABLE ({delta:+.1f}%)"

def churn(rows):
    events = []
    for i in range(1, len(rows)):
        prev, curr = rows[i-1].get("validators", 0), rows[i].get("validators", 0)
        if prev and curr and prev != curr:
            events.append({
                "at": rows[i]["iso"],
                "from": prev,
                "to": curr,
                "delta": curr - prev
            })
    joins = sum(1 for e in events if e["delta"] > 0)
    leaves = sum(1 for e in events if e["delta"] < 0)
    return {
        "activation_events": joins,
        "deactivation_events": leaves,
        "net_change": sum(e["delta"] for e in events),
        "events": events[-5:]  # last 5 for display
    }

def analyze():
    rows = load_history()
    if len(rows) < 10:
        return {"error": "insufficient history"}
    tps = [r["tps"] for r in rows]
    price = [r["price_usd"] for r in rows]
    n_tps = len(tps)
    return {
        "samples": len(rows),
        "span_hours": round((rows[-1]["ts"] - rows[0]["ts"]) / 3600, 1),
        "tps": {
            "sma_short": sma(tps, max(2, n_tps // 4)),
            "sma_long": sma(tps, max(4, n_tps // 2)),
            "trend_24h_proxy": direction(tps),
            "min": min(tps), "max": max(tps)
        },
        "price": {
            "trend": direction(price),
            "min": min(price), "max": max(price)
        },
        "validator_churn": churn(rows)
    }

if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2))
