"""
PHASE 9 — Marriage Story Engine.

Angles: family introductions, trust, connections, relationships. Requires
extra care -- this is the most sensitive content category. Keep it warm,
respectful, and light on specifics that could feel presumptuous about
anyone's real family situation.
"""

from _story_engine_base import run_story_prompt, BASE_VOICE_RULES

MARRIAGE_ANGLES = ["family_introductions", "trust", "connections", "relationships"]


def generate(angle: str = "family_introductions") -> dict:
    task = f"""
Write a marriage-themed post with the angle: "{angle}".
Tone note (important): warm and respectful, never presumptuous, never
joking about marriage/matchmaking in a way that could feel dismissive of
how personal this topic is for people. Focus on the trust mechanism --
families and communities have always been the original "matchmaking
network" -- and how Bataiyo digitizes that same trust, rather than
replacing it with an algorithm or a swipe interface.
Keep it understated. This category should feel like the gentlest post
Bataiyo makes, not the most attention-grabbing.
"""
    return run_story_prompt(BASE_VOICE_RULES, task)


if __name__ == "__main__":
    import json
    print(json.dumps(generate("family_introductions"), indent=2, ensure_ascii=False))
