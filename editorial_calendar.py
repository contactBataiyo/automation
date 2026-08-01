"""
PHASE 3 — Editorial calendar: a default content category per weekday, so
there's a recognizable rhythm (followers start to expect "Trust Tip Friday"
etc), while still allowing content_categories.weighted_choice() as a fallback
and manual overrides for festivals/news-jacking.
"""

import datetime

WEEKDAY_DEFAULTS = {
    0: "educational",           # Monday
    1: "recommendation_story",  # Tuesday
    2: "provider_story",        # Wednesday
    3: "jobs",                  # Thursday
    4: "trust_tip",             # Friday
    5: "festival",              # Saturday
    6: "poll",                  # Sunday
}


def get_category_for_today(override: str = None, date: datetime.date = None) -> str:
    """
    override: pass a content_type id to force it for today (e.g. a festival
              or breaking news day) regardless of the weekday default.
    date: optional, defaults to today -- useful for scheduling ahead/testing.
    """
    if override:
        return override
    d = date or datetime.date.today()
    return WEEKDAY_DEFAULTS[d.weekday()]
