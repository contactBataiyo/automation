"""
STRATEGY ENGINE — the piece the spec was missing.

Everything upstream of this file (trends, categories, calendar) hands it
raw ingredients. Everything downstream (content_gen, story engines) treats
its output as instructions, not a suggestion.

The question it answers, every single day, BEFORE any content is written:

    "If you were the Head of Marketing at Bataiyo, what should today's
     post accomplish?"

It picks ONE primary objective from a fixed list (so the output is always
actionable, never a vague vibe), using the editorial calendar's category as
a hint, learning.py's performance data as evidence, and Gemini as the
reasoning layer that weighs it all like a human strategist would.
"""

import os
import json
import datetime
from google import genai
from knowledge_base import BRAND, PILLARS, PRINCIPLES

_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
_MODEL_NAME = "gemini-3.6-flash"

OBJECTIVES = {
    "increase_downloads": "Drive direct app installs — content should make the value obvious enough to act on now.",
    "educate_users": "Teach the audience how Bataiyo actually works or why word-of-mouth beats the alternative.",
    "build_trust": "Reinforce credibility and the zero-ads/zero-fake-reviews/zero-commission promise, no hard ask.",
    "increase_referrals": "Get existing users to share Bataiyo or tag someone who needs it.",
    "support_providers": "Speak to service providers specifically — earnings, fairness, discoverability.",
    "celebrate_moment": "A festival, cultural moment, or news event worth acknowledging in Bataiyo's voice.",
    "community_story": "Humanize the brand through a real-feeling story about trust/recommendation in a community.",
    "drive_engagement": "Get comments/shares/saves — polls, questions, relatable moments. Lower funnel priority, higher reach priority.",
}


def decide_strategy(editorial_category: str, learning_signals: dict = None, trend_topics: list = None) -> dict:
    """
    Returns:
    {
        "objective": one of OBJECTIVES keys,
        "reasoning": str,
        "target_audience": one of knowledge_base.AUDIENCES keys,
        "preferred_pillar": one of knowledge_base.PILLARS keys or null,
        "content_type_override": optional content_categories id, or null
                                   (lets strategy override the editorial
                                   calendar's default if there's a good reason)
        "cta_goal": one of knowledge_base.CTA_LIBRARY keys
    }
    """
    today = datetime.date.today()
    learning_block = ""
    if learning_signals:
        learning_block = (
            "\nRecent performance signals (use to inform, don't over-index on small samples):\n"
            f"{json.dumps(learning_signals, indent=2)}\n"
        )
    trends_block = ""
    if trend_topics:
        trends_block = "\nToday's available trending topics:\n" + "\n".join(f"- {t}" for t in trend_topics[:10])

    prompt = f"""
You are the Head of Marketing at {BRAND['name']}.

Mission: {BRAND['mission']}
Positioning: {BRAND['positioning']}
Brand principles: {'; '.join(p['statement'] for p in PRINCIPLES)}

Today is {today.strftime('%A, %B %d, %Y')}.
The editorial calendar's default content category for today is: "{editorial_category}".
{learning_block}{trends_block}

Before any content gets written, decide what TODAY's single post should
accomplish. Pick exactly ONE primary objective from this fixed list:
{json.dumps(OBJECTIVES, indent=2)}

Think like a strategist, not a content generator: what does the brand
actually need right now -- more installs, more trust, more provider
sign-ups, more shares? Don't default to "increase_downloads" every day --
a trust-building or educational day is often the right call, and constant
hard-selling burns out an audience.

Respond ONLY with valid JSON, no markdown fences:
{{
  "objective": "one of the objective keys above",
  "reasoning": "2-3 sentences: why this objective, today, given the calendar/signals/trends",
  "target_audience": "one of: homeowners, students, parents, professionals, businesses, providers",
  "preferred_pillar": "one of: trusted_recommendations, services, jobs, marriage, communities",
  "content_type_override": "a content_categories.py content type id if you want to override today's default, else null",
  "cta_goal": "one of: increase_downloads, educate, build_trust, increase_referrals, help_providers, engagement"
}}
"""
    response = _client.models.generate_content(model="gemini-3.6-flash", contents=prompt)
    text = response.text.strip().strip("```json").strip("```").strip()
    try:
        strategy = json.loads(text)
    except json.JSONDecodeError:
        print(f"[strategy_engine] Failed to parse model output, falling back to safe default:\n{text}")
        strategy = {
            "objective": "build_trust",
            "reasoning": "Fallback default -- model output failed to parse.",
            "target_audience": "homeowners",
            "preferred_pillar": "trusted_recommendations",
            "content_type_override": None,
            "cta_goal": "build_trust",
        }

    if strategy.get("objective") not in OBJECTIVES:
        print(f"[strategy_engine] Unknown objective '{strategy.get('objective')}', defaulting to build_trust")
        strategy["objective"] = "build_trust"

    return strategy


if __name__ == "__main__":
    print(json.dumps(decide_strategy("educational", trend_topics=["Diwali home cleaning trends"]), indent=2))
