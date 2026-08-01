"""
Shared plumbing for the story engines (recommendation_story, before_internet,
community_story, job_story, marriage_story). Not a phase on its own -- just
avoids repeating the same Gemini call + JSON parsing five times.

Every story engine returns the same shape so content_gen.py can treat them
interchangeably:
{
    "headline": str,
    "hook": str,
    "caption": str,
    "hashtags": [str],
    "cta": str,
    "image_prompt": str,
    "reel_script": str,
    "carousel_slides": [str, ...]
}
"""

import os
import json
from google import genai
from knowledge_base import BRAND, HASHTAGS_BASE

_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
_MODEL_NAME = "gemini-2.0-flash"

OUTPUT_SCHEMA = """
Respond ONLY with valid JSON, no markdown fences:
{
  "headline": "punchy on-image headline, max 8 words",
  "hook": "first line of the caption -- must earn the rest of the read",
  "caption": "full caption, 2-4 short paragraphs, natural voice, no clickbait, no generic AI phrasing",
  "hashtags": ["#tag1", "#tag2"],
  "cta": "one soft call to action matching the story's spirit",
  "image_prompt": "plain descriptive scene prompt, no color instructions",
  "reel_script": "short voiceover/on-screen-text script if this suits a reel, else empty string",
  "carousel_slides": ["short line for slide 1", "short line for slide 2", "..."]
}
"""


def run_story_prompt(system_context: str, task: str) -> dict:
    prompt = f"{system_context}\n\n{task}\n\n{OUTPUT_SCHEMA}"
    response = _client.models.generate_content(model=_MODEL_NAME, contents=prompt)
    text = response.text.strip().strip("```json").strip("```").strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        print(f"[story_engine] Failed to parse output:\n{text}")
        return None
    data["hashtags"] = list(dict.fromkeys(data.get("hashtags", []) + HASHTAGS_BASE))
    return data


BASE_VOICE_RULES = f"""
You are writing social content for {BRAND['name']} ({BRAND['tagline']}).
Voice: {BRAND['tone']}
Rules: never hard-sell, always educate or tell a genuine story first, use
storytelling over statistics, create curiosity, end with a soft CTA, avoid
clickbait and generic AI phrasing ("in today's fast-paced world", "unlock
the power of", etc). Write like a person, not a marketing department.
"""
