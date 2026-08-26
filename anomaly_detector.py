#!/usr/bin/env python3
"""
Solana Ecosystem Pulse — Anomaly Detection Engine
Evaluates telemetry vectors and detects network anomalies:
- TPS throughput degradation
- Validator delinquency spikes
- Nakamoto coefficient decentralization risks
- DeFi TVL & price shock deviations
"""

from typing import Dict, Any, List


class AnomalyDetector:
    def __init__(self):
        # Configurable thresholds
        self.TPS_WARN_THRESHOLD = 2000.0
        self.TPS_CRIT_THRESHOLD = 1000.0
        self.DELINQUENT_STAKE_WARN_PCT = 1.5
        self.DELINQUENT_STAKE_CRIT_PCT = 5.0
        self.NAKAMOTO_WARN_THRESHOLD = 15
        self.NAKAMOTO_CRIT_THRESHOLD = 10
        self.PRICE_VOLATILITY_PCT = 7.5
        self.TVL_CHANGE_WARN_PCT = 5.0

    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        anomalies: List[Dict[str, Any]] = []
        overall_severity = "HEALTHY"  # HEALTHY, WARNING, CRITICAL

        net = data.get("network_performance", {})
        val = data.get("validators", {})
        eco = data.get("economics", {})
        defi = data.get("defi", {})

        # 1. TPS Throughput Check
        avg_tps = net.get("avg_tps_30m", 0.0)
        curr_tps = net.get("current_tps", 0.0)
        if curr_tps < self.TPS_CRIT_THRESHOLD:
            anomalies.append({
                "metric": "TPS Throughput",
                "severity": "CRITICAL",
                "value": f"{curr_tps} TPS",
                "description": f"Severe network throughput slowdown detected ({curr_tps} < {self.TPS_CRIT_THRESHOLD} TPS)."
            })
            overall_severity = "CRITICAL"
        elif curr_tps < self.TPS_WARN_THRESHOLD:
            anomalies.append({
                "metric": "TPS Throughput",
                "severity": "WARNING",
                "value": f"{curr_tps} TPS",
                "description": f"Moderate TPS dip below optimal benchmark ({curr_tps} < {self.TPS_WARN_THRESHOLD} TPS)."
            })
            if overall_severity != "CRITICAL":
                overall_severity = "WARNING"

        # 2. Validator Delinquency Check
        delinq_pct = val.get("delinquent_stake_pct", 0.0)
        delinq_count = val.get("delinquent_validators", 0)
        if delinq_pct > self.DELINQUENT_STAKE_CRIT_PCT:
            anomalies.append({
                "metric": "Validator Delinquency",
                "severity": "CRITICAL",
                "value": f"{delinq_pct}% ({delinq_count} nodes)",
                "description": f"Critical stake delinquency spike ({delinq_pct}% > {self.DELINQUENT_STAKE_CRIT_PCT}% threshold)."
            })
            overall_severity = "CRITICAL"
        elif delinq_pct > self.DELINQUENT_STAKE_WARN_PCT:
            anomalies.append({
                "metric": "Validator Delinquency",
                "severity": "WARNING",
                "value": f"{delinq_pct}% ({delinq_count} nodes)",
                "description": f"Elevated delinquent stake ({delinq_pct}% > {self.DELINQUENT_STAKE_WARN_PCT}% threshold)."
            })
            if overall_severity != "CRITICAL":
                overall_severity = "WARNING"

        # 3. Decentralization / Nakamoto Coefficient
        nakamoto = val.get("nakamoto_coefficient", 0)
        if nakamoto < self.NAKAMOTO_CRIT_THRESHOLD:
            anomalies.append({
                "metric": "Nakamoto Coefficient",
                "severity": "CRITICAL",
                "value": f"{nakamoto}",
                "description": f"Severe stake centralization risk! Minimum nodes to halt network: {nakamoto}."
            })
            overall_severity = "CRITICAL"
        elif nakamoto < self.NAKAMOTO_WARN_THRESHOLD:
            anomalies.append({
                "metric": "Nakamoto Coefficient",
                "severity": "WARNING",
                "value": f"{nakamoto}",
                "description": f"Suboptimal stake dispersion ({nakamoto} < {self.NAKAMOTO_WARN_THRESHOLD})."
            })
            if overall_severity != "CRITICAL":
                overall_severity = "WARNING"

        # 4. Economic & Price Volatility
        price_change = eco.get("change_24h_pct", 0.0)
        if abs(price_change) >= self.PRICE_VOLATILITY_PCT:
            anomalies.append({
                "metric": "SOL 24h Volatility",
                "severity": "WARNING",
                "value": f"{price_change:+.2f}%",
                "description": f"High market volatility detected: SOL price moved {price_change:+.2f}% in 24h."
            })
            if overall_severity != "CRITICAL":
                overall_severity = "WARNING"

        # 5. TVL Inflow / Outflow
        tvl_change = defi.get("tvl_change_24h_pct", 0.0)
        if abs(tvl_change) >= self.TVL_CHANGE_WARN_PCT:
            anomalies.append({
                "metric": "DeFi TVL Shift",
                "severity": "WARNING",
                "value": f"{tvl_change:+.2f}%",
                "description": f"Substantial ecosystem capital migration: 24h TVL shifted by {tvl_change:+.2f}%."
            })
            if overall_severity != "CRITICAL":
                overall_severity = "WARNING"

        # 6. Data source health (from cross-source verification block)
        pv = data.get("price_verification", {})
        if pv.get("error"):
            anomalies.append({
                "metric": "Price Feed Integrity",
                "severity": "WARNING",
                "value": "sources degraded",
                "description": f"Cross-source price check failed: {pv['error']}. Market data may be stale."
            })
            if overall_severity != "CRITICAL":
                overall_severity = "WARNING"
        elif pv.get("sources_up", 3) < 2:
            anomalies.append({
                "metric": "Price Feed Integrity",
                "severity": "WARNING",
                "value": f"{pv.get('sources_up')}/3 sources up",
                "description": "Multiple price sources down — running on reduced redundancy."
            })
            if overall_severity != "CRITICAL":
                overall_severity = "WARNING"
        elif pv.get("verdict") == "DIVERGENCE":
            anomalies.append({
                "metric": "Cross-Market Divergence",
                "severity": "CRITICAL",
                "value": f"{pv.get('spread_pct')}% spread",
                "description": f"Severe price divergence across venues: {pv.get('prices')}. Possible arbitrage or stale feed."
            })
            overall_severity = "CRITICAL"

        # Health Score computation (0 - 100)
        health_score = 100
        for a in anomalies:
            if a["severity"] == "CRITICAL":
                health_score -= 30
            elif a["severity"] == "WARNING":
                health_score -= 10
        health_score = max(0, min(100, health_score))

        return {
            "overall_status": overall_severity,
            "ecosystem_health_score": health_score,
            "anomaly_count": len(anomalies),
            "anomalies": anomalies
        }


if __name__ == "__main__":
    from data_pipeline import SolanaDataPipeline
    p = SolanaDataPipeline()
    d = p.run_full_aggregation()
    detector = AnomalyDetector()
    res = detector.analyze(d)
    print("Anomaly Detection Results:")
    print(f"Health Score: {res['ecosystem_health_score']}/100 | Status: {res['overall_status']}")
    print(f"Detected Anomalies ({res['anomaly_count']}):")
    for item in res["anomalies"]:
        print(f"  [{item['severity']}] {item['metric']}: {item['description']}")
