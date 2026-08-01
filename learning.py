"""
PHASE 12 — Learning.

Reads analytics.py's history and produces two things main.py feeds forward:

1. content_type_weight_overrides -- for content_categories.weighted_choice(),
   so high-performing content types get picked more often over time.
2. A plain-language signals summary -- fed into strategy_engine's prompt so
   the "Head of Marketing" reasoning has real evidence, not just vibes.

Deliberately simple (average engagement_rate per group, minimum sample size
before trusting a signal) -- this is meant to nudge, not to overfit on a
handful of early posts.
"""

from collections import defaultdict
import analytics

MIN_SAMPLES = 3  # don't trust a signal from fewer posts than this


def _avg_engagement_by(field: str) -> dict:
    rows = [r for r in analytics.load_all() if r.get("engagement_rate")]
    grouped = defaultdict(list)
    for r in rows:
        key = r.get(field)
        if key:
            grouped[key].append(float(r["engagement_rate"]))
    return {k: sum(v) / len(v) for k, v in grouped.items() if len(v) >= MIN_SAMPLES}


def get_content_type_weight_overrides(base_weight=15) -> dict:
    """Returns {content_type_id: new_weight} for the best/worst performers only
    -- content_categories.weighted_choice() falls back to defaults for anything
    not returned here."""
    perf = _avg_engagement_by("content_type")
    if not perf:
        return {}
    avg_of_avgs = sum(perf.values()) / len(perf)
    overrides = {}
    for content_type, rate in perf.items():
        if rate > avg_of_avgs * 1.3:
            overrides[content_type] = int(base_weight * 1.5)
        elif rate < avg_of_avgs * 0.7:
            overrides[content_type] = max(1, int(base_weight * 0.5))
    return overrides


def get_learning_signals_summary() -> dict:
    """Plain-language-ready signals for strategy_engine's prompt."""
    return {
        "top_content_types_by_engagement": _avg_engagement_by("content_type"),
        "top_pillars_by_engagement": _avg_engagement_by("pillar"),
        "top_audiences_by_engagement": _avg_engagement_by("audience"),
        "note": "Rates are averages; only shown for groups with >= "
                f"{MIN_SAMPLES} published posts with recorded insights.",
    }


if __name__ == "__main__":
    import json
    print(json.dumps(get_learning_signals_summary(), indent=2))
    print(json.dumps(get_content_type_weight_overrides(), indent=2))
