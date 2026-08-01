"""
PHASE 7 — Community Story Engine.

Stories centered on a community (neighbourhood, parents, schools, doctors,
teachers, local businesses) rather than an individual -- reinforces the
"community first" principle.
"""

from _story_engine_base import run_story_prompt, BASE_VOICE_RULES

COMMUNITIES = ["neighbourhood", "parents", "schools", "doctors", "teachers", "local businesses"]


def generate(community: str = "neighbourhood") -> dict:
    task = f"""
Write a community story post centered on: {community}.
Focus on how good information/recommendations move through this specific
community when it works well (a parents' WhatsApp group knowing the best
tutor, a neighbourhood knowing the reliable electrician, doctors trusting
each other's referrals). Make it feel like a real, specific slice of life
for this community, not a generic "communities are great" statement.
Land on how Bataiyo is built to capture and extend exactly this kind of
community knowledge, without turning it into another impersonal platform.
"""
    return run_story_prompt(BASE_VOICE_RULES, task)


if __name__ == "__main__":
    import json
    print(json.dumps(generate("parents"), indent=2, ensure_ascii=False))
