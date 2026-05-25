# ingestion/sources/registry.py

SOURCE_REGISTRY = {
    # ── Tier 1 — Global wire services (highest credibility) ──
    "reuters.com":              {"tier": 1, "credibility": 0.95, "region": "global"},
    "apnews.com":               {"tier": 1, "credibility": 0.94, "region": "global"},
    "bloomberg.com":            {"tier": 1, "credibility": 0.94, "region": "global"},
    "bbc.com":                  {"tier": 1, "credibility": 0.92, "region": "global"},
    "bbc.co.uk":                {"tier": 1, "credibility": 0.92, "region": "global"},
    "theguardian.com":          {"tier": 1, "credibility": 0.90, "region": "global"},
    "nytimes.com":              {"tier": 1, "credibility": 0.91, "region": "US"},
    "wsj.com":                  {"tier": 1, "credibility": 0.91, "region": "US"},
    "ft.com":                   {"tier": 1, "credibility": 0.92, "region": "global"},
    "economist.com":            {"tier": 1, "credibility": 0.91, "region": "global"},

    # ── Tier 2 — Major Indian outlets ──
    "thehindu.com":             {"tier": 2, "credibility": 0.88, "region": "IN"},
    "livemint.com":             {"tier": 2, "credibility": 0.86, "region": "IN"},
    "business-standard.com":    {"tier": 2, "credibility": 0.85, "region": "IN"},
    "economictimes.com":        {"tier": 2, "credibility": 0.84, "region": "IN"},
    "economictimes.indiatimes.com": {"tier": 2, "credibility": 0.84, "region": "IN"},
    "hindustantimes.com":       {"tier": 2, "credibility": 0.83, "region": "IN"},
    "ndtv.com":                 {"tier": 2, "credibility": 0.83, "region": "IN"},
    "timesofindia.com":         {"tier": 2, "credibility": 0.82, "region": "IN"},
    "indianexpress.com":        {"tier": 2, "credibility": 0.84, "region": "IN"},
    "thewire.in":               {"tier": 2, "credibility": 0.80, "region": "IN"},
    "scroll.in":                {"tier": 2, "credibility": 0.79, "region": "IN"},

    # ── Tier 2 — Major US outlets ──
    "washingtonpost.com":       {"tier": 2, "credibility": 0.88, "region": "US"},
    "nbcnews.com":              {"tier": 2, "credibility": 0.85, "region": "US"},
    "abcnews.go.com":           {"tier": 2, "credibility": 0.84, "region": "US"},
    "cbsnews.com":              {"tier": 2, "credibility": 0.84, "region": "US"},
    "npr.org":                  {"tier": 2, "credibility": 0.88, "region": "US"},
    "politico.com":             {"tier": 2, "credibility": 0.83, "region": "US"},
    "thehill.com":              {"tier": 2, "credibility": 0.80, "region": "US"},

    # ── Tier 3 — Tech and business outlets ──
    "techcrunch.com":           {"tier": 3, "credibility": 0.78, "region": "US"},
    "wired.com":                {"tier": 3, "credibility": 0.79, "region": "US"},
    "venturebeat.com":          {"tier": 3, "credibility": 0.72, "region": "US"},
    "forbes.com":               {"tier": 3, "credibility": 0.74, "region": "US"},
    "businessinsider.com":      {"tier": 3, "credibility": 0.72, "region": "US"},
    "cnbc.com":                 {"tier": 3, "credibility": 0.76, "region": "US"},
    "cnn.com":                  {"tier": 3, "credibility": 0.75, "region": "US"},
    "foxnews.com":              {"tier": 3, "credibility": 0.60, "region": "US"},
    "theverge.com":             {"tier": 3, "credibility": 0.75, "region": "US"},
    "arstechnica.com":          {"tier": 3, "credibility": 0.78, "region": "US"},
    "mashable.com":             {"tier": 3, "credibility": 0.68, "region": "US"},

    # ── Tier 3 — Indian business and tech ──
    "moneycontrol.com":         {"tier": 3, "credibility": 0.76, "region": "IN"},
    "financialexpress.com":     {"tier": 3, "credibility": 0.77, "region": "IN"},
    "theprint.in":              {"tier": 3, "credibility": 0.76, "region": "IN"},
    "medianama.com":            {"tier": 3, "credibility": 0.72, "region": "IN"},
    "inc42.com":                {"tier": 3, "credibility": 0.70, "region": "IN"},
    "yourstory.com":            {"tier": 3, "credibility": 0.68, "region": "IN"},

    # ── Tier 4 — Aggregators and lower credibility ──
    "zeenews.india.com":        {"tier": 4, "credibility": 0.58, "region": "IN"},
    "news18.com":               {"tier": 4, "credibility": 0.58, "region": "IN"},
    "aajtak.in":                {"tier": 4, "credibility": 0.55, "region": "IN"},
    "indiatoday.in":            {"tier": 4, "credibility": 0.65, "region": "IN"},
    "opindia.com":              {"tier": 4, "credibility": 0.40, "region": "IN"},
    "swarajyamag.com":          {"tier": 4, "credibility": 0.45, "region": "IN"},
    "breitbart.com":            {"tier": 4, "credibility": 0.35, "region": "US"},
    "dailymail.co.uk":          {"tier": 4, "credibility": 0.45, "region": "GB"},
    "nypost.com":               {"tier": 4, "credibility": 0.50, "region": "US"},
}

FALLBACK_SOURCE = {"tier": 4, "credibility": 0.50, "region": "unknown"}


def get_source_meta(url: str) -> dict:
    """Extract domain from URL and return credibility metadata."""
    try:
        from urllib.parse import urlparse
        domain = urlparse(url).netloc.replace("www.", "")
        # also try without subdomain — e.g. feeds.reuters.com → reuters.com
        base_domain = ".".join(domain.split(".")[-2:])
        return (
            SOURCE_REGISTRY.get(domain) or
            SOURCE_REGISTRY.get(base_domain) or
            FALLBACK_SOURCE
        )
    except Exception:
        return FALLBACK_SOURCE