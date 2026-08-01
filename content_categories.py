"""
PHASE 2 — Content category rotation.

Instead of the model freely picking a format every time, we define the set
of content types Bataiyo posts, each with a weight, and pick one via
weighted random selection (optionally biased later by learning.py based on
what's actually performing).
"""

import random

CONTENT_TYPES = [
    {"id": "educational", "weight": 20, "engine": "generic"},
    {"id": "recommendation_story", "weight": 20, "engine": "recommendation_story"},
    {"id": "customer_story", "weight": 8, "engine": "generic"},
    {"id": "provider_story", "weight": 10, "engine": "generic"},
    {"id": "community_story", "weight": 8, "engine": "community_story"},
    {"id": "before_internet", "weight": 8, "engine": "before_internet"},
    {"id": "trust_tip", "weight": 6, "engine": "generic"},
    {"id": "faq", "weight": 4, "engine": "generic"},
    {"id": "jobs", "weight": 5, "engine": "job_story"},
    {"id": "marriage", "weight": 3, "engine": "marriage_story"},
    {"id": "festival", "weight": 3, "engine": "generic"},
    {"id": "local_news", "weight": 2, "engine": "generic"},
    {"id": "poll", "weight": 1, "engine": "generic"},
    {"id": "meme", "weight": 1, "engine": "generic"},
    {"id": "founder_opinion", "weight": 1, "engine": "generic"},
]

assert sum(c["weight"] for c in CONTENT_TYPES) == 100, "CONTENT_TYPES weights must sum to 100"


def weighted_choice(weight_overrides: dict = None, exclude: list = None) -> dict:
    """
    weight_overrides: optional {content_type_id: new_weight} from learning.py,
                       lets high performers get picked more often over time.
    exclude: content_type ids to skip entirely for this pick.
    """
    pool = [c for c in CONTENT_TYPES if not exclude or c["id"] not in exclude]
    weights = [
        (weight_overrides or {}).get(c["id"], c["weight"])
        for c in pool
    ]
    return random.choices(pool, weights=weights, k=1)[0]


def get_by_id(content_type_id: str) -> dict:
    return next((c for c in CONTENT_TYPES if c["id"] == content_type_id), None)
