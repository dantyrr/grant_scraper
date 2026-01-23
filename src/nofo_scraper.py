"""NIH Guide RSS feed parser for NOFOs (Notices of Funding Opportunities)."""

import feedparser
from datetime import datetime, timedelta
from time import mktime
from typing import Optional

from .config import NIH_GUIDE_RSS_URL, KEYWORDS, DAYS_LOOKBACK


def fetch_rss_feed(url: str = NIH_GUIDE_RSS_URL) -> list[dict]:
    """Fetch and parse the NIH Guide RSS feed."""
    try:
        feed = feedparser.parse(url)
        if feed.bozo and feed.bozo_exception:
            print(f"RSS feed parsing warning: {feed.bozo_exception}")
        return feed.entries
    except Exception as e:
        print(f"Error fetching RSS feed: {e}")
        return []


def filter_by_date(entries: list[dict], days_back: int = DAYS_LOOKBACK) -> list[dict]:
    """Filter entries to only include those from the last N days."""
    cutoff_date = datetime.now() - timedelta(days=days_back)
    filtered = []

    for entry in entries:
        # Try to parse publication date
        pub_date = None
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            pub_date = datetime.fromtimestamp(mktime(entry.published_parsed))
        elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
            pub_date = datetime.fromtimestamp(mktime(entry.updated_parsed))

        if pub_date and pub_date >= cutoff_date:
            entry["parsed_date"] = pub_date
            filtered.append(entry)

    return filtered


def calculate_relevance_score(entry: dict, keywords: list[str] = KEYWORDS) -> int:
    """Calculate relevance score based on keyword matches."""
    score = 0
    title = (entry.get("title") or "").lower()
    summary = (entry.get("summary") or "").lower()

    for keyword in keywords:
        kw_lower = keyword.lower()
        if kw_lower in title:
            score += 3
        if kw_lower in summary:
            score += 1

    return score


def filter_by_keywords(entries: list[dict], keywords: list[str] = KEYWORDS) -> list[dict]:
    """Filter entries that match at least one keyword and add relevance scores."""
    matching = []

    for entry in entries:
        score = calculate_relevance_score(entry, keywords)
        if score > 0:
            entry["relevance_score"] = score
            matching.append(entry)

    # Sort by relevance score
    matching.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
    return matching


def fetch_nofos(keywords: Optional[list[str]] = None) -> list[dict]:
    """Fetch NOFOs matching keywords from the last week."""
    if keywords is None:
        keywords = KEYWORDS

    # Fetch RSS feed
    entries = fetch_rss_feed()

    # Filter by date
    recent_entries = filter_by_date(entries)

    # Filter by keywords
    matching_entries = filter_by_keywords(recent_entries, keywords)

    return matching_entries


def format_nofo_for_display(nofo: dict) -> dict:
    """Format a single NOFO for display in the digest."""
    pub_date = nofo.get("parsed_date")
    if pub_date:
        pub_date_str = pub_date.strftime("%Y-%m-%d")
    else:
        pub_date_str = nofo.get("published", "Unknown date")

    return {
        "title": nofo.get("title", "No title"),
        "link": nofo.get("link", "#"),
        "published": pub_date_str,
        "summary": nofo.get("summary", "No summary available"),
        "relevance_score": nofo.get("relevance_score", 0)
    }
