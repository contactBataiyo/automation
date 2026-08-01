"""
PHASE 8 — Jobs Engine.

Angles: referral, career, networking, hiring, mentorship -- all rooted in
the same core idea as the rest of the brand (real people vouching for real
people), applied to careers instead of services.
"""

from _story_engine_base import run_story_prompt, BASE_VOICE_RULES

JOB_ANGLES = ["referral", "career", "networking", "hiring", "mentorship"]


def generate(angle: str = "referral", audience: str = "professionals") -> dict:
    task = f"""
Write a jobs-themed post with the angle: "{angle}".
Audience: {audience}.
Keep the same brand mechanism as everything else Bataiyo posts -- real
people vouching for real people -- but applied to careers: a referral that
led somewhere, the awkwardness of asking for one, how hiring through trusted
networks beats a resume pile, or a mentorship connection that mattered.
Land naturally on how Bataiyo extends this same trust mechanism to job
discovery, not just services.
"""
    return run_story_prompt(BASE_VOICE_RULES, task)


if __name__ == "__main__":
    import json
    print(json.dumps(generate("referral"), indent=2, ensure_ascii=False))
