#!/usr/bin/env python3
"""
Superteam Earn Sniper — polls new listings, filters by relevance, alerts via Telegram.
Runs alongside pipeline_loop. Checks every 60s.
"""
import json, time, pathlib, urllib.request

BASE = pathlib.Path(__file__).parent
STATE = BASE / "sniper_state.json"
LOG = BASE / "sniper_alerts.jsonl"

# Known listing slugs at deploy time (baseline to avoid alert storm)
KNOWN_SEED = [
    "develop-solana-ecosystem-auto-updating-report-and-interactive-dashboard",
    "provide-a-report-on-solana-communities-based-on-direct-engagement",
    "dollar1000-usdc-manic-bug-bounty", "fairscale-ansem", "aeonianbounty",
    "nectarfi-x-dominion-market", "zns-sol", "trade-tweet-and-earn-1",
    "ideathon-submit-innovative-ideas-for-the-hackathon",
    "compose-x-thread-explaining-segmento-and-on-chain-user-intelligence",
    "mato-research-how-do-you-actually-trade-on-solana",
    "share-solana-startup-terminal-referral-link",
    "superteam-nepal-ambassador-campaign", "kriptok-league-content-bounty",
    "draft-x-thread-detailing-la-ccf-and-its-shows-in-spanish",
    "twitter-post-about-nft-locks-on-streamflow",
    "create-the-best-x-thread-about-my-crypto-casino",
    "why-digital-credit-matters",
    "solana-summit-canada-creator-challenge-part-1",
    "create-content-for-breakpoint-2026", "solana-summit-serbia-content",
    "superteam-nepal-creator-bounty-the-superteam-story",
    "creator-program-tell-the-story-that-brings-thailands-next-talent-to-solana",
    "bounty-de-conteudo-documente-a-hackathon-universitaria-no-instagram",
    "hackathon-universitaria-superteam-brasil-1",
    "create-content-to-engage-new-builders-for-the-hackathon",
    "post-why-flint-beats-building-your-own-prop-amm",
]

# Relevance keywords — higher score = more interesting for us
KEYWORDS = {
    "develop": 3, "build": 3, "dashboard": 3, "api": 3, "bot": 3,
    "data": 2, "analytic": 2, "monitor": 2, "script": 2, "code": 2,
    "research": 2, "report": 2, "technical": 2,
    "content": -1, "tweet": -1, "video": -1, "design": -2, "meme": -2,
}

TELEGRAM_TOKEN = ""  # set env var or fill here; empty = log-only mode
TELEGRAM_CHAT = ""

def fetch_listing_slugs():
    """Scrape current listing inventory from the SSR mirror."""
    try:
        req = urllib.request.Request(
            "https://r.jina.ai/https://superteam.fun/earn/bounties/",
            headers={"User-Agent": "Pulse/1.0"})
        html = urllib.request.urlopen(req, timeout=45).read().decode()
        import re
        return set(re.findall(r'/earn/listing/([a-z0-9-]+)', html))
    except Exception:
        return set()

def score_slug(slug):
    s = slug.lower()
    return sum(w for k, w in KEYWORDS.items() if k in s)

def load_state():
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {"known": KNOWN_SEED}

def save_state(st):
    STATE.write_text(json.dumps(st))

def alert(slug, score):
    entry = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
             "slug": slug, "relevance_score": score,
             "url": f"https://superteam.fun/earn/listing/{slug}"}
    with open(LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"🆕 NEW LISTING: {slug} (relevance: {score:+d})")
    print(f"   → {entry['url']}")

def tick():
    st = load_state()
    known = set(st["known"])
    current = fetch_listing_slugs()
    if not current:
        return  # scrape failed silently, retry next tick
    new_slugs = current - known
    for slug in sorted(new_slugs):
        sc = score_slug(slug)
        alert(slug, sc)
    st["known"] = sorted(known | current)
    save_state(st)

if __name__ == "__main__":
    print("Earn sniper started. Polling every 90s...")
    while True:
        try:
            tick()
        except Exception as e:
            print(f"tick error: {e}")
        time.sleep(90)
