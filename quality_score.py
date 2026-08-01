"""
PHASE 18 — Content Quality Score.

Before publishing, have the model score its own output against a rubric
and reject anything below threshold. This is a second, independent pass --
it evaluates the finished post, not the generation process, which catches
things like a technically-on-brief post that just reads badly.
"""

import os
import json
from google import genai
from knowledge_base import BRAND

_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
_MODEL_NAME = "gemini-2.0-flash"

THRESHOLD = int(os.environ.get("QUALITY_THRESHOLD", 80))

RUBRIC = {
    "headline": "Sharp, specific, makes someone want to read on (not generic). Max 20 points.",
    "hook": "Earns the rest of the read, doesn't waste the first line. Max 15 points.",
    "caption": "Natural voice, no clickbait, no generic AI phrasing, actually says something. Max 25 points.",
    "cta": "Fits the post's spirit, not a bolted-on hard sell. Max 10 points.",
    "trend_relevance": "If a trend was used, the bridge is genuinely clever, not forced. N/A scores full marks. Max 15 points.",
    "brand_relevance": f"Clearly and correctly represents {BRAND['name']}'s actual positioning, nothing invented. Max 15 points.",
}


def score_post(idea: dict) -> dict:
    """
    Returns:
    {
        "total": int (0-100),
        "breakdown": {criterion: score},
        "pass": bool,
        "feedback": str
    }
    """
    prompt = f"""
You are a strict but fair editor scoring a social media post before it's
allowed to publish for {BRAND['name']}.

Rubric (score each, then sum to a 0-100 total):
{json.dumps(RUBRIC, indent=2)}

Post to score:
Headline: {idea.get('headline')}
Hook: {idea.get('hook')}
Caption: {idea.get('caption')}
CTA: {idea.get('cta')}
Trend used: {idea.get('trend_used') or 'none'}
Trend bridge reasoning: {idea.get('reasoning') or 'n/a'}

Respond ONLY with valid JSON:
{{
  "breakdown": {{"headline": int, "hook": int, "caption": int, "cta": int, "trend_relevance": int, "brand_relevance": int}},
  "total": int,
  "feedback": "1-2 sentences on the biggest thing that would improve this post, or 'strong as-is' if genuinely no notes"
}}
"""
    response = _client.models.generate_content(model=_MODEL_NAME, contents=prompt)
    text = response.text.strip().strip("```json").strip("```").strip()
    try:
        result = json.loads(text)
    except json.JSONDecodeError:
        print(f"[quality_score] parse failed, failing safe (reject):\n{text}")
        return {"total": 0, "breakdown": {}, "pass": False, "feedback": "Scoring failed to parse -- rejected safe."}

    result["pass"] = result.get("total", 0) >= THRESHOLD
    return result
