"""
PHASE 10 — trends.py, expanded.

Sources (all free, no paid keys):
- Google Trends India (daily trending searches)
- Reddit hot posts (r/india, r/smallbusiness)
- Google News RSS (scoped queries: home services, gig economy, jobs, weddings)
- A small static festival calendar (India) for "celebrate_moment" strategy days
- Basic tech/startup India news via Google News RSS

Adds:
- Topic scoring (freshness + source-weight, simple and transparent)
- Duplicate detection against a same-run seen-set (case-insensitive substring)
- A rough `category` tag per trend, used as a hint (not a hard rule) by
  content_gen.py when picking a pillar
"""

import datetime
import requests
import feedparser
from pytrends.request import TrendReq

SOURCE_WEIGHTS = {
    "google_trends": 1.0,
    "reddit_r_india": 0.8,
    "reddit_r_smallbusiness": 0.8,
    "news_home_services": 0.9,
    "news_jobs": 0.9,
    "news_weddings": 0.7,
    "news_startup_india": 0.6,
    "festival_calendar": 1.0,
}

# Minimal static festival calendar -- extend as needed. Month/day, India-relevant.
FESTIVAL_CALENDAR = [
    {"month": 1, "day": 14, "name": "Makar Sankranti / Pongal"},
    {"month": 1, "day": 26, "name": "Republic Day"},
    {"month": 3, "day": 8, "name": "Holi (approx, verify yearly)"},
    {"month": 8, "day": 15, "name": "Independence Day"},
    {"month": 10, "day": 2, "name": "Gandhi Jayanti"},
    {"month": 10, "day": 20, "name": "Diwali (approx, verify yearly)"},
]


def get_google_trends_india(limit=10):
    try:
        pytrends = TrendReq(hl="en-IN", tz=330)
        df = pytrends.trending_searches(pn="india")
        topics = df[0].tolist()[:limit]
        return [{"source": "google_trends", "topic": t, "category": "general"} for t in topics]
    except Exception as e:
        print(f"[trends] Google Trends fetch failed: {e}")
        return []


def get_reddit_hot(subreddit, limit=10, category="general"):
    url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}"
    headers = {"User-Agent": "bataiyo-trend-bot/0.2"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        posts = resp.json()["data"]["children"]
        return [
            {
                "source": f"reddit_r_{subreddit}",
                "topic": p["data"]["title"],
                "category": category,
                "extra": {"score": p["data"]["score"]},
            }
            for p in posts
        ]
    except Exception as e:
        print(f"[trends] Reddit r/{subreddit} fetch failed: {e}")
        return []


def get_google_news(query, source_id, category, limit=8):
    """Free Google News RSS -- no key needed."""
    url = f"https://news.google.com/rss/search?q={requests.utils.quote(query)}&hl=en-IN&gl=IN&ceid=IN:en"
    try:
        feed = feedparser.parse(url)
        return [
            {
                "source": source_id,
                "topic": entry.title,
                "category": category,
                "extra": {"published": entry.get("published", "")},
            }
            for entry in feed.entries[:limit]
        ]
    except Exception as e:
        print(f"[trends] Google News fetch failed for '{query}': {e}")
        return []


def get_festival_of_the_moment(window_days=10):
    today = datetime.date.today()
    upcoming = []
    for f in FESTIVAL_CALENDAR:
        try:
            this_year = today.replace(month=f["month"], day=f["day"])
        except ValueError:
            continue
        delta = (this_year - today).days
        if 0 <= delta <= window_days:
            upcoming.append({
                "source": "festival_calendar",
                "topic": f["name"],
                "category": "festival",
                "extra": {"days_away": delta},
            })
    return upcoming


def _score(trend: dict) -> float:
    """Simple, transparent scoring: source weight, boosted for imminent festivals
    and high-score Reddit posts. Not ML -- deliberately inspectable."""
    base = SOURCE_WEIGHTS.get(trend["source"], 0.5)
    if trend.get("extra", {}).get("score"):
        base += min(trend["extra"]["score"] / 5000, 0.3)
    if trend.get("extra", {}).get("days_away") is not None:
        base += (10 - trend["extra"]["days_away"]) * 0.05
    return round(base, 3)


def _dedupe(trends: list) -> list:
    seen = set()
    out = []
    for t in trends:
        key = t["topic"].strip().lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(t)
    return out


def get_all_trends():
    trends = []
    trends += get_google_trends_india()
    trends += get_reddit_hot("india", category="general")
    trends += get_reddit_hot("smallbusiness", category="business")
    trends += get_google_news("home services India", "news_home_services", "services")
    trends += get_google_news("jobs hiring India", "news_jobs", "jobs")
    trends += get_google_news("wedding vendors India", "news_weddings", "marriage")
    trends += get_google_news("India startup news", "news_startup_india", "general")
    trends += get_festival_of_the_moment()

    trends = _dedupe(trends)
    for t in trends:
        t["score"] = _score(t)
    trends.sort(key=lambda t: t["score"], reverse=True)
    return trends


if __name__ == "__main__":
    for t in get_all_trends()[:15]:
        print(f"{t['score']:.2f}  [{t['source']}]  {t['topic']}")
