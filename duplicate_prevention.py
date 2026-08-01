"""
PHASE 15 — Duplicate prevention.

Never post the same topic, headline, or near-identical caption within a
configurable window (default 60 days). Keeps its own lightweight JSON
history file rather than reusing analytics.py's CSV, since this needs to
run BEFORE publishing (analytics.py logs AFTER publishing).
"""

import os
import json
import datetime
import difflib

HISTORY_PATH = os.environ.get("DUPLICATE_HISTORY_PATH", "analytics/post_history.json")
DEFAULT_WINDOW_DAYS = 60
SIMILARITY_THRESHOLD = 0.82  # difflib ratio above this = "too similar"


def _load_history() -> list:
    if not os.path.exists(HISTORY_PATH):
        return []
    with open(HISTORY_PATH) as f:
        return json.load(f)


def _save_history(history: list):
    os.makedirs(os.path.dirname(HISTORY_PATH), exist_ok=True)
    with open(HISTORY_PATH, "w") as f:
        json.dump(history, f, indent=2)


def _recent(history: list, window_days: int) -> list:
    cutoff = datetime.date.today() - datetime.timedelta(days=window_days)
    return [h for h in history if datetime.date.fromisoformat(h["date"]) >= cutoff]


def is_duplicate(headline: str, caption: str, topic: str = None, window_days=DEFAULT_WINDOW_DAYS) -> bool:
    history = _recent(_load_history(), window_days)
    for h in history:
        if topic and h.get("topic") and topic.strip().lower() == h["topic"].strip().lower():
            return True
        if difflib.SequenceMatcher(None, headline.lower(), h["headline"].lower()).ratio() > SIMILARITY_THRESHOLD:
            return True
        if difflib.SequenceMatcher(None, caption.lower(), h["caption"].lower()).ratio() > SIMILARITY_THRESHOLD:
            return True
    return False


def record_post(headline: str, caption: str, topic: str = None):
    history = _load_history()
    history.append({
        "date": datetime.date.today().isoformat(),
        "headline": headline,
        "caption": caption,
        "topic": topic or "",
    })
    _save_history(history)
