"""
PHASE 6 — "Before Internet" Series.

Theme: people trusted people, before platforms inserted themselves in
between. Contrasts a pre-platform era with today's ad/review/algorithm-driven
discovery, landing on Bataiyo as a return to the original mechanism, digitized.
"""

from _story_engine_base import run_story_prompt, BASE_VOICE_RULES

REFERENCE_POINTS = [
    "Before Google Reviews", "Before LinkedIn", "Before Zomato",
    "Before Practo", "Before JustDial", "Before Swiggy",
]


def generate(reference_point: str = None) -> dict:
    ref = reference_point or REFERENCE_POINTS[0]
    task = f"""
Write a "Before Internet" post using the angle: "{ref}".
Theme: people trusted people. Before this platform existed, how did people
actually find a good doctor / restaurant / job / service? Through someone
who knew someone. Make the contrast specific and a little nostalgic/witty,
not preachy -- then land on: that original mechanism (real people vouching
for real people) is exactly what Bataiyo digitizes, without becoming another
platform full of paid placements and fake reviews itself.
Avoid trashing the named platform -- the point is about the mechanism
(algorithms/ads vs. people), not a competitor callout.
"""
    return run_story_prompt(BASE_VOICE_RULES, task)


if __name__ == "__main__":
    import json
    print(json.dumps(generate("Before Google Reviews"), indent=2, ensure_ascii=False))
