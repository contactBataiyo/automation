"""
PHASE 4 — content_gen.py, rewritten.

OLD flow: Trend -> find matching problem -> generate caption.

NEW flow:
    Strategy (from strategy_engine)
        -> Content category (from editorial_calendar / content_categories)
            -> Trend (optional -- not every post needs one)
                -> Knowledge base: pillar + problem + audience
                    -> Route to a story engine OR generic generation
                        -> hook, headline, caption, cta, image_prompt
                            -> structured JSON

Never hardcodes brand facts -- everything brand-related comes from
knowledge_base.py. This file's job is orchestration + prompting, not being
a source of truth.
"""

import os
import json
import time
from google import genai

import knowledge_base as kb
import content_categories as cc
import recommendation_story
import before_internet
import community_story
import job_story
import marriage_story

_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
MODEL_NAME = "gemini-3.6-flash"

STORY_ENGINES = {
    "recommendation_story": recommendation_story,
    "before_internet": before_internet,
    "community_story": community_story,
    "job_story": job_story,
    "marriage_story": marriage_story,
}

GENERIC_SYSTEM_CONTEXT = f"""
You are the social media strategist for {kb.BRAND['name']}.

Mission: {kb.BRAND['mission']}
Positioning: {kb.BRAND['positioning']}
Voice: {kb.BRAND['tone']}
Brand principles: {'; '.join(p['statement'] for p in kb.PRINCIPLES)}

Never claim {kb.BRAND['name']} does anything outside its actual pillars:
{', '.join(v['label'] for v in kb.PILLARS.values())}.

Rules for every post: never hard-sell, always educate or tell a genuine
story first, use storytelling over statistics, create curiosity, end with a
soft CTA, avoid clickbait and generic AI phrasing. Write like a person.
"""


def _pick_problem_for_strategy(strategy: dict, trend: dict = None) -> dict:
    """Filter PROBLEMS by the strategy's preferred pillar, and let the model
    pick the single best match given the trend (if any) and strategy objective."""
    pillar = strategy.get("preferred_pillar")
    candidates = [p for p in kb.PROBLEMS if not pillar or p["pillar"] == pillar] or kb.PROBLEMS

    trend_line = f'Trending topic to consider bridging to: "{trend.get("topic")}"' if trend else "No trend input for this post -- pick the strongest evergreen problem for today's objective."

    prompt = f"""{GENERIC_SYSTEM_CONTEXT}

Today's strategic objective: {strategy['objective']} -- {strategy_engine_desc(strategy['objective'])}
Target audience: {strategy.get('target_audience')}
{trend_line}

Candidate problems (pick exactly one by id):
{json.dumps(candidates, indent=2)}

Respond ONLY with valid JSON: {{"problem_id": "...", "trend_relevant": true/false, "bridge_reasoning": "1-2 sentences"}}
If a trend was given but doesn't genuinely bridge to any candidate problem,
set "trend_relevant": false and still pick the best evergreen problem_id --
we'll simply skip using the trend for this post, not skip the post itself.
"""
    response = _client.models.generate_content(model=_MODEL_NAME, contents=prompt)
    text = response.text.strip().strip("```json").strip("```").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        print(f"[content_gen] problem-pick parse failed:\n{text}")
        return {"problem_id": candidates[0]["id"], "trend_relevant": False, "bridge_reasoning": "fallback"}


def strategy_engine_desc(objective_id):
    from strategy_engine import OBJECTIVES
    return OBJECTIVES.get(objective_id, "")


def _generic_generate(problem: dict, strategy: dict, content_type: str, trend: dict = None) -> dict:
    trend_line = f'Weave in this trend if it genuinely fits: "{trend.get("topic")}"' if trend else ""
    cta_options = kb.CTA_LIBRARY.get(strategy.get("cta_goal", "build_trust"), kb.CTA_LIBRARY["build_trust"])

    prompt = f"""{GENERIC_SYSTEM_CONTEXT}

Content type for this post: {content_type}
Today's objective: {strategy['objective']}
Target audience: {strategy.get('target_audience')}
Problem this post addresses: {problem['problem']}
Bataiyo's angle: {problem['bataiyo_angle']}
{trend_line}
Pick or adapt a CTA in this spirit (don't quote verbatim, match the tone): {cta_options}

Respond ONLY with valid JSON, no markdown fences:
{{
  "headline": "punchy on-image headline, max 8 words",
  "hook": "first line of the caption",
  "caption": "2-4 short paragraphs, natural voice",
  "hashtags": ["#tag1", "#tag2"],
  "cta": "final CTA line",
  "image_prompt": "plain descriptive scene prompt, no color instructions",
  "format": "single_image" or "carousel" or "reel",
  "slide_headlines": ["short line per slide, only if carousel/reel"],
  "reel_voiceover_script": "only if format is reel, else empty string"
}}
"""
for attempt in range(3):
    try:
        response = _client.models.generate_content(model=MODEL_NAME, contents=prompt)
        break
    except Exception as e:
        if any(err in str(e) for err in ["503", "429", "RESOURCE_EXHAUSTED", "UNAVAILABLE"]):
            print(f"[content_gen] API busy/rate-limited. Waiting 15s (attempt {attempt + 1}/3)...")
            time.sleep(15)
        else:
            raise e    
            text = response.text.strip().strip("```json").strip("```").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        print(f"[content_gen] generic generation parse failed:\n{text}")
        return None


def generate_post(strategy: dict, content_type_id: str, trend: dict = None) -> dict:
    """
    Main entry point. Returns the structured post dict (or None if generation
    failed) matching the schema:
    { headline, hook, caption, hashtags, cta, image_prompt, content_type,
      pillar, problem, audience, format, slide_headlines, reel_voiceover_script }
    """
    pick = _pick_problem_for_strategy(strategy, trend)
    problem = kb.get_problem(pick["problem_id"])
    if not problem:
        print(f"[content_gen] Unknown problem_id {pick['problem_id']}, aborting.")
        return None

    content_type = cc.get_by_id(content_type_id) or cc.get_by_id("educational")
    engine_name = content_type["engine"]

    if engine_name in STORY_ENGINES:
        engine = STORY_ENGINES[engine_name]
        if engine_name == "recommendation_story":
            result = engine.generate(problem["id"], audience=strategy.get("target_audience", "homeowners"))
        elif engine_name == "before_internet":
            result = engine.generate()
        elif engine_name == "community_story":
            result = engine.generate()
        elif engine_name in ("job_story", "marriage_story"):
            result = engine.generate()
        else:
            result = None
        if result:
            result["format"] = "carousel" if result.get("carousel_slides") else "single_image"
    else:
        result = _generic_generate(problem, strategy, content_type_id, trend)

    if not result:
        return None

    result["content_type"] = content_type_id
    result["pillar"] = problem["pillar"]
    result["problem"] = problem["id"]
    result["audience"] = strategy.get("target_audience")
    result["hashtags"] = list(dict.fromkeys(result.get("hashtags", []) + kb.HASHTAGS_BASE))
    result["relevant"] = True
    result["reasoning"] = pick.get("bridge_reasoning", "")
    result["trend_used"] = trend.get("topic") if (trend and pick.get("trend_relevant")) else None
    return result


if __name__ == "__main__":
    sample_strategy = {
        "objective": "build_trust",
        "target_audience": "homeowners",
        "preferred_pillar": "services",
        "cta_goal": "build_trust",
    }
    print(json.dumps(generate_post(sample_strategy, "educational"), indent=2, ensure_ascii=False))
