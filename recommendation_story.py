"""
PHASE 5 — Recommendation Story Engine.

Generates realistic, small, believable stories about a recommendation
mattering -- the emotional core of Bataiyo's whole pitch. Deliberately
mundane/specific (an electrician, a tutor) rather than grand claims --
specificity is what makes these feel real instead of like ad copy.
"""

from _story_engine_base import run_story_prompt, BASE_VOICE_RULES
from knowledge_base import get_problem


def generate(problem_id: str, audience: str = "homeowners") -> dict:
    problem = get_problem(problem_id)
    task = f"""
Write a "recommendation story" post: a small, specific, believable moment
where a personal recommendation solved a real problem -- in the spirit of
"My neighbour recommended an electrician. That recommendation saved me two
days. Trust spreads through people."

Ground it in this specific problem: {problem['problem'] if problem else 'finding a trustworthy service provider'}
Audience to write for: {audience}
Keep it small and specific (a name-less neighbour/friend/colleague, a
concrete situation) -- not a grand statement about the whole company.
End by connecting it, briefly and naturally, to how Bataiyo digitizes
exactly this kind of moment.
"""
    return run_story_prompt(BASE_VOICE_RULES, task)


if __name__ == "__main__":
    import json
    print(json.dumps(generate("trusted_electricians"), indent=2, ensure_ascii=False))
