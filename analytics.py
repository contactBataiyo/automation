"""
PHASE 11 — Analytics.

CSV is acceptable initially per spec; swap for SQLite later by replacing
the read/write functions below -- callers (learning.py, main.py) don't need
to change.

Two halves:
1. log_post() -- called right after publishing, records what was posted.
2. fetch_and_update_insights() -- called some time later (a separate,
   scheduled run) to pull actual engagement numbers from the Graph API and
   fill them into the same row. Engagement isn't available immediately
   after posting, so this is deliberately a separate step.
"""

import os
import csv
import datetime
import requests

CSV_PATH = os.environ.get("ANALYTICS_CSV_PATH", "analytics/posts.csv")

FIELDS = [
    "post_id", "published_date", "content_type", "topic", "audience",
    "pillar", "problem", "format", "platform",
    "reach", "likes", "comments", "shares", "saves", "watch_time",
    "ctr", "engagement_rate", "insights_fetched_at",
]


def _ensure_csv():
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    if not os.path.exists(CSV_PATH):
        with open(CSV_PATH, "w", newline="") as f:
            csv.DictWriter(f, fieldnames=FIELDS).writeheader()


def log_post(post_id: str, idea: dict, platform: str):
    """Call right after a successful publish_meta/publish_linkedin call."""
    _ensure_csv()
    row = {f: "" for f in FIELDS}
    row.update({
        "post_id": post_id,
        "published_date": datetime.date.today().isoformat(),
        "content_type": idea.get("content_type", ""),
        "topic": idea.get("trend_used") or "",
        "audience": idea.get("audience", ""),
        "pillar": idea.get("pillar", ""),
        "problem": idea.get("problem", ""),
        "format": idea.get("format", ""),
        "platform": platform,
    })
    with open(CSV_PATH, "a", newline="") as f:
        csv.DictWriter(f, fieldnames=FIELDS).writerow(row)


def fetch_and_update_insights(ig_user_id: str, access_token: str, min_hours_since_post=24):
    """
    Pulls Instagram Graph API insights (reach, likes, comments, shares, saves)
    for any logged post older than `min_hours_since_post` that doesn't have
    insights recorded yet, and updates the CSV in place.

    Run this on a separate, later schedule (e.g. once/day, covering
    yesterday's posts) -- not immediately after publishing.
    """
    _ensure_csv()
    rows = []
    with open(CSV_PATH) as f:
        rows = list(csv.DictReader(f))

    now = datetime.datetime.utcnow()
    for row in rows:
        if row["insights_fetched_at"] or not row["post_id"]:
            continue
        published = datetime.datetime.fromisoformat(row["published_date"])
        if (now - published).total_seconds() < min_hours_since_post * 3600:
            continue
        try:
            resp = requests.get(
                f"https://graph.facebook.com/v19.0/{row['post_id']}/insights",
                params={
                    "metric": "reach,likes,comments,shares,saved,total_interactions",
                    "access_token": access_token,
                },
                timeout=15,
            ).json()
            metrics = {m["name"]: m["values"][0]["value"] for m in resp.get("data", [])}
            row["reach"] = metrics.get("reach", "")
            row["likes"] = metrics.get("likes", "")
            row["comments"] = metrics.get("comments", "")
            row["shares"] = metrics.get("shares", "")
            row["saves"] = metrics.get("saved", "")
            reach = metrics.get("reach") or 0
            interactions = metrics.get("total_interactions") or 0
            row["engagement_rate"] = round(interactions / reach, 4) if reach else ""
            row["insights_fetched_at"] = now.isoformat()
        except Exception as e:
            print(f"[analytics] Insight fetch failed for {row['post_id']}: {e}")

    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def load_all() -> list:
    _ensure_csv()
    with open(CSV_PATH) as f:
        return list(csv.DictReader(f))
