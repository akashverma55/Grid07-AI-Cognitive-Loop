import re
from langchain_core.tools import tool


# ── Sandboxed Mock News Database ───────────────────────────────────────────────

_MOCK_NEWS_DB: dict[str, str] = {
    "ai": (
        "OpenAI releases GPT-5 with reasoning that outperforms PhD-level humans. "
        "Anthropic raises $4B to build next-gen safety-focused AI. "
        "EU AI Act enforcement begins — companies scramble to comply."
    ),
    "crypto": (
        "Bitcoin hits new all-time high of $120,000 amid regulatory ETF approvals. "
        "Ethereum Layer 2 adoption surges as gas fees hit record lows. "
        "SEC approves spot Ethereum ETF, crypto markets rally 30%."
    ),
    "elon": (
        "Elon Musk's xAI launches Grok-3, claims it beats all competitors. "
        "SpaceX Starship completes first crewed Mars flyby mission. "
        "Tesla Full Self-Driving achieves Level 5 autonomy certification."
    ),
    "tech": (
        "Apple unveils Vision Pro 2 with neural interface capabilities. "
        "Google DeepMind solves protein folding for all known diseases. "
        "Nvidia H200 GPU demand causes 18-month supply shortage."
    ),
    "markets": (
        "Fed holds rates steady at 4.5% amid mixed inflation signals. "
        "S&P 500 hits all-time high as tech earnings beat expectations. "
        "Goldman Sachs predicts AI boom will add 7% to global GDP."
    ),
    "trading": (
        "Quant hedge funds post 40% returns using AI-powered algorithms. "
        "High-frequency trading now accounts for 70% of all equity volume. "
        "New SEC regulations target dark pool trading transparency."
    ),
    "capitalism": (
        "Income inequality hits record high as billionaire wealth doubles. "
        "Amazon workers unionize in 12 new warehouses across the US. "
        "Big Tech antitrust trial results in landmark $50B breakup order."
    ),
    "privacy": (
        "Meta fined $2B for illegal facial recognition data collection in EU. "
        "Apple's new feature blocks 95% of cross-app tracking. "
        "TikTok banned in 15 countries over data sovereignty concerns."
    ),
    "space": (
        "NASA confirms water ice deposits large enough to sustain a Mars colony. "
        "SpaceX launches 1000th Starlink satellite achieving global coverage. "
        "China and US sign historic space cooperation treaty."
    ),
    "ev": (
        "Tesla Model Y battery retains 94% capacity after 150,000 miles. "
        "EV sales surpass gasoline cars for first time in European market. "
        "New solid-state battery promises 1000-mile range and 10-minute charging."
    ),
    "regulation": (
        "EU passes sweeping AI regulation affecting all models above 10B parameters. "
        "US Congress introduces bipartisan AI liability bill. "
        "China tightens control over generative AI with new content rules."
    ),
    "social media": (
        "X/Twitter loses 30% of advertisers following content moderation rollbacks. "
        "Instagram introduces mandatory screen time limits for users under 18. "
        "New study links social media algorithms to increased political polarization."
    ),
}

_DEFAULT_RESULT = (
    "Breaking: Global markets react to latest geopolitical developments. "
    "Tech sector leads gains as AI investment continues to surge. "
    "Analysts predict major industry shifts over the next 12 months."
)


def _sanitize_query(query: str) -> str:
    query = query[:200].lower()
    return "".join(c for c in query if c.isalnum() or c in " .,?-").strip()


@tool
def mock_searxng_search(query: str) -> str:
    clean_query = _sanitize_query(query)

    if not clean_query:
        return _DEFAULT_RESULT

    for keyword, results in _MOCK_NEWS_DB.items():
        if keyword in clean_query:
            return results

    return _DEFAULT_RESULT