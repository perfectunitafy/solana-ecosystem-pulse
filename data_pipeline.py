#!/usr/bin/env python3
"""
Solana Ecosystem Pulse — Data Aggregation Pipeline
Extracts on-chain & off-chain metrics without requiring private API keys.
Data Sources:
  1. Solana Public JSON-RPC (getEpochInfo, getRecentPerformanceSamples, getVoteAccounts, getSupply, getVersion)
  2. DeFiLlama Free REST API (Solana TVL, protocol breakdown, stablecoin mcap)
  3. CoinGecko / Public Coin API (SOL price, 24h volume, mcap, 24h delta)
"""

import json
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, Any, List, Optional

SOLANA_RPCS = [
    "https://api.mainnet-beta.solana.com",
    "https://solana-mainnet.rpc.extrnode.com",
    "https://rpc.ankr.com/solana"
]

DEFILLAMA_TVL_URL = "https://api.llama.fi/v2/historicalChainTvl/Solana"
DEFILLAMA_PROTOCOLS_URL = "https://api.llama.fi/protocols"

# Keyless market-data sources (geo-friendly order): OKX -> DexScreener -> CoinGecko
OKX_TICKER_URL = "https://www.okx.com/api/v5/market/ticker?instId=SOL-USDT"
DEXSCREENER_SOL_URL = "https://api.dexscreener.com/latest/dex/tokens/So11111111111111111111111111111111111111112"
COINGECKO_PRICE_URL = "https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd"

HEADERS = {"User-Agent": "SolanaEcosystemPulse/1.0 (OpenSource Bounty Edition)"}


def fetch_json(url: str, timeout: int = 15, headers: Optional[Dict[str, str]] = None) -> Optional[Any]:
    req = urllib.request.Request(url, headers=headers or HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        # Silently return None so fallbacks trigger
        return None
    return None


def rpc_call(method: str, params: Optional[List[Any]] = None, timeout: int = 20) -> Optional[Any]:
    payload = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params or []
    }).encode("utf-8")
    
    headers = {"Content-Type": "application/json", "User-Agent": "SolanaEcosystemPulse/1.0"}
    
    for rpc_url in SOLANA_RPCS:
        req = urllib.request.Request(rpc_url, data=payload, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    if "result" in data:
                        return data["result"]
        except Exception:
            continue
    return None


HISTORY_FILE = "history.jsonl"
HISTORY_MAX_POINTS = 5760  # ~24h at 15s interval


def append_history_snapshot(data: Dict[str, Any]) -> None:
    """Appends a compact metrics snapshot to history.jsonl for time-series charts."""
    try:
        snap = {
            "ts": data["meta"]["timestamp"],
            "iso": data["meta"]["generated_at_utc"],
            "tps": data["network_performance"]["current_tps"],
            "avg_tps_30m": data["network_performance"]["avg_tps_30m"],
            "tvl_usd": data["defi"]["tvl_usd"],
            "price_usd": data["economics"]["price_usd"],
            "validators": data["validators"]["active_validators"],
        }
        base = Path(__file__).parent / HISTORY_FILE
        lines = []
        if base.exists():
            lines = base.read_text().splitlines()
        lines.append(json.dumps(snap))
        # Keep only the most recent N points (24h rolling window)
        if len(lines) > HISTORY_MAX_POINTS:
            lines = lines[-HISTORY_MAX_POINTS:]
        tmp = base.with_suffix(".tmp")
        tmp.write_text("\n".join(lines) + "\n")
        tmp.replace(base)
    except Exception as e:
        print(f"[history] snapshot failed: {e}")


class SolanaDataPipeline:
    def __init__(self):
        self.timestamp = int(time.time())

    def get_network_performance(self) -> Dict[str, Any]:
        """Calculates true TPS, slot time, and epoch progression."""
        epoch_info = rpc_call("getEpochInfo") or {}
        samples = rpc_call("getRecentPerformanceSamples", [30]) or []
        version_info = rpc_call("getVersion") or {}
        
        # Calculate real-time TPS from samples
        tps_list = []
        sample_durations = []
        if samples:
            for s in samples:
                num_tx = s.get("numTransactions", 0)
                sec = s.get("samplePeriodSecs", 60)
                if sec > 0:
                    tps_list.append(round(num_tx / sec, 1))
                    sample_durations.append(sec)

        avg_tps = round(sum(tps_list) / len(tps_list), 1) if tps_list else 0.0
        max_tps = max(tps_list) if tps_list else 0.0
        min_tps = min(tps_list) if tps_list else 0.0
        
        epoch = epoch_info.get("epoch", 0)
        slot_index = epoch_info.get("slotIndex", 0)
        slots_in_epoch = epoch_info.get("slotsInEpoch", 432000)
        epoch_progress_pct = round((slot_index / slots_in_epoch) * 100, 2) if slots_in_epoch else 0.0
        
        # Estimate remaining epoch time (400ms target slot)
        slots_remaining = slots_in_epoch - slot_index
        est_hours_remaining = round((slots_remaining * 0.45) / 3600, 1)

        return {
            "epoch": epoch,
            "absolute_slot": epoch_info.get("absoluteSlot", 0),
            "block_height": epoch_info.get("blockHeight", 0),
            "slot_index": slot_index,
            "slots_in_epoch": slots_in_epoch,
            "epoch_progress_pct": epoch_progress_pct,
            "est_hours_remaining": est_hours_remaining,
            "current_tps": tps_list[0] if tps_list else avg_tps,
            "avg_tps_30m": avg_tps,
            "min_tps_30m": min_tps,
            "max_tps_30m": max_tps,
            "recent_tps_samples": tps_list[:15],
            "solana_core_version": version_info.get("solana-core", "2.1.x"),
            "feature_set": version_info.get("feature-set", 0)
        }

    def get_validator_metrics(self) -> Dict[str, Any]:
        """Aggregates active vs delinquent validators, stake concentration (Nakamoto coefficient)."""
        vote_accounts = rpc_call("getVoteAccounts") or {}
        current = vote_accounts.get("current", [])
        delinquent = vote_accounts.get("delinquent", [])
        
        total_current_stake_lamports = sum(v.get("activatedStake", 0) for v in current)
        total_delinquent_stake_lamports = sum(v.get("activatedStake", 0) for v in delinquent)
        total_stake_lamports = total_current_stake_lamports + total_delinquent_stake_lamports
        
        total_current_stake_sol = round(total_current_stake_lamports / 1e9, 2)
        total_delinquent_stake_sol = round(total_delinquent_stake_lamports / 1e9, 2)
        delinquent_stake_pct = round((total_delinquent_stake_lamports / total_stake_lamports) * 100, 3) if total_stake_lamports else 0.0

        # Sort validators by active stake to compute top concentration
        sorted_validators = sorted(current, key=lambda x: x.get("activatedStake", 0), reverse=True)
        
        # Calculate Nakamoto coefficient (min validators to control >33.33% stake)
        cumulative_stake = 0
        threshold_stake = total_stake_lamports * 0.33334
        nakamoto_coefficient = 0
        for v in sorted_validators:
            cumulative_stake += v.get("activatedStake", 0)
            nakamoto_coefficient += 1
            if cumulative_stake >= threshold_stake:
                break
                
        # Top 5 Validators
        top_5_validators = []
        for v in sorted_validators[:5]:
            stake_sol = round(v.get("activatedStake", 0) / 1e9, 2)
            stake_pct = round((v.get("activatedStake", 0) / total_stake_lamports) * 100, 2) if total_stake_lamports else 0.0
            top_5_validators.append({
                "vote_pubkey": v.get("votePubkey", "")[:8] + "..." + v.get("votePubkey", "")[-6:],
                "node_pubkey": v.get("nodePubkey", "")[:8] + "...",
                "stake_sol": stake_sol,
                "stake_pct": stake_pct,
                "commission_pct": v.get("commission", 0)
            })

        return {
            "active_validators": len(current),
            "delinquent_validators": len(delinquent),
            "total_validators": len(current) + len(delinquent),
            "total_active_stake_sol": total_current_stake_sol,
            "total_delinquent_stake_sol": total_delinquent_stake_sol,
            "delinquent_stake_pct": delinquent_stake_pct,
            "nakamoto_coefficient": nakamoto_coefficient,
            "top_5_validators": top_5_validators
        }

    def get_token_economics(self) -> Dict[str, Any]:
        """Fetches SOL price, market cap, 24h volume and supply metrics."""
        supply_info = rpc_call("getSupply", [{"excludeNonCirculatingAccountsList": True}]) or {}
        supply_val = supply_info.get("value", {})
        
        total_supply_sol = round(supply_val.get("total", 0) / 1e9, 2)
        circulating_sol = round(supply_val.get("circulating", 0) / 1e9, 2)
        non_circulating_sol = round(supply_val.get("nonCirculating", 0) / 1e9, 2)
        
        # Fetch Price Data — keyless cascade: OKX → DexScreener → CoinGecko
        price_usd = 0.0
        change_24h_pct = 0.0
        volume_24h_usd = 0.0
        market_cap_usd = 0.0
        price_source = "n/a"

        okx = fetch_json(OKX_TICKER_URL)
        if okx and okx.get("data"):
            t = okx["data"][0]
            last = float(t.get("last", 0) or 0)
            open24h = float(t.get("open24h", 0) or 0)
            vol24h = float(t.get("volCcy24h", 0) or 0)
            if last > 0:
                price_usd = round(last, 2)
                change_24h_pct = round(((last - open24h) / open24h) * 100, 2) if open24h else 0.0
                volume_24h_usd = round(vol24h * last, 2)
                market_cap_usd = round(price_usd * circulating_sol, 2)
                price_source = "OKX"

        if price_usd == 0.0:
            dx = fetch_json(DEXSCREENER_SOL_URL)
            pairs = [p for p in (dx or {}).get("pairs", [])
                     if p.get("quoteToken", {}).get("symbol") in ("USDC", "USDT")]
            if pairs:
                p = max(pairs, key=lambda x: float(x.get("liquidity", {}).get("usd") or 0))
                price_usd = round(float(p.get("priceUsd") or 0), 2)
                volume_24h_usd = round(float(p.get("volume", {}).get("h24") or 0), 2)
                pc = p.get("priceChange", {}).get("h24")
                change_24h_pct = round(float(pc), 2) if pc is not None else 0.0
                market_cap_usd = round(price_usd * circulating_sol, 2)
                price_source = "DexScreener"

        if price_usd == 0.0:
            cg = fetch_json(COINGECKO_PRICE_URL)
            if cg and "solana" in cg:
                price_usd = round(cg["solana"].get("usd", 0.0), 2)
                market_cap_usd = round(price_usd * circulating_sol, 2)
                price_source = "CoinGecko" 

        return {
            "price_usd": price_usd,
            "change_24h_pct": change_24h_pct,
            "volume_24h_usd": volume_24h_usd,
            "market_cap_usd": market_cap_usd,
            "price_source": price_source,
            "total_supply_sol": total_supply_sol,
            "circulating_sol": circulating_sol,
            "non_circulating_sol": non_circulating_sol
        }

    def get_defi_metrics(self) -> Dict[str, Any]:
        """Fetches Solana TVL, 24h change, and top 5 ecosystem protocols from DeFiLlama."""
        # Historical TVL for accurate 24h delta
        hist = fetch_json(DEFILLAMA_TVL_URL) or []
        tvl_usd = round(hist[-1].get("tvl", 0.0), 2) if hist else 0.0
        tvl_prev = round(hist[-2].get("tvl", hist[-1].get("tvl", 0.0)), 2) if len(hist) > 1 else tvl_usd
        tvl_change_24h_pct = round(((tvl_usd - tvl_prev) / tvl_prev) * 100, 2) if tvl_prev else 0.0
        # TVL trend over last 7 days
        week_ago = round(hist[-8].get("tvl", tvl_usd), 2) if len(hist) >= 8 else tvl_usd
        tvl_change_7d_pct = round(((tvl_usd - week_ago) / week_ago) * 100, 2) if week_ago else 0.0
        tvl_history_7d = [{"date": h["date"], "tvl": h["tvl"]} for h in hist[-7:]] if hist else []
        
        # Protocols breakdown
        protocols = fetch_json(DEFILLAMA_PROTOCOLS_URL) or []
        sol_protocols = []
        for p in protocols:
            chain_tvls = p.get("chainTvls", {})
            if "Solana" in chain_tvls:
                sol_protocols.append({
                    "name": p.get("name", ""),
                    "category": p.get("category", ""),
                    "tvl_solana_usd": round(chain_tvls["Solana"], 2),
                    "change_1d": round(p.get("change_1d", 0.0) or 0.0, 2)
                })
        
        top_protocols = sorted(sol_protocols, key=lambda x: x["tvl_solana_usd"], reverse=True)[:6]

        return {
            "tvl_usd": tvl_usd,
            "tvl_change_24h_pct": tvl_change_24h_pct,
            "tvl_change_7d_pct": tvl_change_7d_pct,
            "tvl_history_7d": tvl_history_7d,
            "top_protocols": top_protocols
        }

    def run_full_aggregation(self) -> Dict[str, Any]:
        """Runs complete on-chain and off-chain data aggregation."""
        network = self.get_network_performance()
        validators = self.get_validator_metrics()
        economics = self.get_token_economics()
        defi = self.get_defi_metrics()
        
        return {
            "meta": {
                "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(self.timestamp)),
                "timestamp": self.timestamp,
                "pipeline_version": "1.0.0",
                "network": "Solana Mainnet-Beta"
            },
            "network_performance": network,
            "validators": validators,
            "economics": economics,
            "defi": defi
        }


if __name__ == "__main__":
    print("Executing Solana Ecosystem Data Pipeline...")
    start = time.time()
    pipeline = SolanaDataPipeline()
    result = pipeline.run_full_aggregation()
    elapsed = round(time.time() - start, 2)
    print(f"Data aggregation completed in {elapsed}s.")
    print(f"Current TPS: {result['network_performance']['current_tps']} | Avg TPS: {result['network_performance']['avg_tps_30m']}")
    print(f"Active Validators: {result['validators']['active_validators']} | Nakamoto Coeff: {result['validators']['nakamoto_coefficient']}")
    print(f"SOL Price: ${result['economics']['price_usd']} | TVL: ${result['defi']['tvl_usd']:,.2f}")
