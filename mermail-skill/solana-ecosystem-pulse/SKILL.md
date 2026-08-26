---
name: solana-ecosystem-pulse
description: Query live Solana network health, validator decentralization, SOL price with cross-source verification, DeFi TVL, and anomaly alerts through public JSON-RPC and free market APIs. Use when the user asks about Solana network status, TPS, epoch progress, validator counts or delinquency, Nakamoto coefficient, SOL price from multiple venues, TVL changes, or wants continuous monitoring with anomaly detection. Do not use for other chains, token-specific trading advice, or private RPC endpoints.
metadata:
  openclaw:
    requires:
      env: []
    homepage: https://github.com/perfectunitafy/solana-ecosystem-pulse
    emoji: "🌐"
---

# Solana Ecosystem Pulse

## Overview

Answer Solana network questions with measured data instead of stale training knowledge. Every value comes from a live query at answer time: network throughput from performance samples (not inflated vote-TX counts), validator decentralization from actual stake distribution, prices verified across three independent venues, TVL from aggregated protocol data.

All sources are free public tiers. No API keys required.

Load references before acting:
- Read [tools.md](references/tools.md) for exact endpoint URLs, request formats, and response fields.
- Read [security.md](references/security.md) before relaying market data into automated actions.

## Preferred Deliverables

- Network answers grounded in one timestamped snapshot: state the `generated_at` time explicitly.
- Price answers naming every source queried and its value, plus the computed spread verdict (COHERENT / MINOR_DRIFT / DIVERGENCE).
- Anomaly reports listing each active check result with severity and threshold breached.
- Trend claims backed by sample count and time span ("over N snapshots / X hours"), never single-point guesses.

## Workflow

1. Determine which question class applies: network performance, validators/decentralization, market price, DeFi TVL, or anomaly status.
2. Call only the endpoints needed for that class. If a source fails, note it and continue with remaining sources — never fabricate a value for a failed call.
3. For price answers, always query at least two independent sources. Report per-source values, the spread in USD and percent, and the coherence verdict. Flag any outlier source deviating >0.15% from median.
4. For trend or history questions, read the accumulated `history.jsonl` snapshot log; state sample count and window span before summarizing direction.
5. Compute the Health Score contribution of any new anomalies found during this session and report it alongside raw values.

## Interpretation Rules

- TPS below 2,000 is WARNING; below 1,000 is CRITICAL. Always compare against the 30-minute average, not the instantaneous value alone.
- Delinquent stake above 1.5% is WARNING; above 5% is CRITICAL. Report both node count and stake percentage.
- A Nakamoto Coefficient under 15 warrants a centralization note; under 10 is a direct risk statement.
- Cross-venue spread over 0.35% is DIVERGENCE — report as possible arbitrage or stale feed before drawing market conclusions.
- Never present a single-source price as verified. Two-source minimum for any actionable claim.

## Output Conventions

- Prefix network answers with the snapshot timestamp in UTC.
- Distinguish measured values from computed ones (e.g., "TPS 3,544 (measured)" vs "Nakamoto Coefficient 18 (computed from current stake distribution)").
- When sources disagree beyond thresholds, show all values side by side rather than picking one.
- End monitoring sessions with the Health Score and a one-line system verdict.

## Example Requests

- "How is the Solana network doing right now?"
- "What's SOL trading at? Is it consistent across exchanges?"
- "Are there any validators falling behind?"
- "How decentralized is Solana staking today?"
- "Has TVL moved in the last day?"
- "Run an anomaly check and give me the health score."
