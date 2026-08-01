"""
main.py — v2 orchestrator.

    Strategy Engine          "what should today's post accomplish?"
        v
    Editorial Calendar       today's default content category
        v
    Content Categories       weighted pick (biased by learning.py)
        v
    Trends                   scored, deduped trend candidates (optional input)
        v
    content_gen               knowledge-base-driven generation / story engines
        v
    Quality Score             reject + retry once if below threshold
        v
    Duplicate Prevention      skip if too similar to last 60 days
        v
    image_gen -> template_render -> video_gen     UNCHANGED, per spec
        v
    publish_meta / publish_linkedin                UNCHANGED, per spec
        v
    Analytics + Duplicate history logging

Run manually: `python main.py`
Run on autopilot: .github/workflows/daily_post.yml
"""

import os

import strategy_engine
import editorial_calendar
import content_categories as cc
import learning
import trends as trends_mod
import content_gen
import quality_score
import duplicate_prevention
import analytics

from image_gen import generate_image, generate_carousel
from template_render import render_feed_slide, render_reel_cover
from video_gen import build_reel
import publish_meta

PUBLIC_HOST_BASE = os.environ.get("PUBLIC_HOST_BASE", "https://YOUR_USERNAME.github.io/bataiyo-media")
OUTPUT_DIR = "output"
RAW_DIR = os.path.join(OUTPUT_DIR, "_raw")
MAX_GENERATION_ATTEMPTS = 3  # across content-type retries, not just quality retries


def build_todays_post(calendar_override: str = None):
    """Runs Strategy -> Calendar -> Category -> Trends -> content_gen, with a
    quality gate + duplicate check. Returns a passing `idea` dict, or None if
    nothing cleared the bar after MAX_GENERATION_ATTEMPTS."""

    all_trends = trends_mod.get_all_trends()
    trend_topics = [t["topic"] for t in all_trends[:15]]

    learning_signals = learning.get_learning_signals_summary()
    weight_overrides = learning.get_content_type_weight_overrides()

    editorial_category = editorial_calendar.get_category_for_today(override=calendar_override)
    strategy = strategy_engine.decide_strategy(editorial_category, learning_signals, trend_topics)
    print(f"[strategy] objective={strategy['objective']}  reasoning={strategy['reasoning']}")

    content_type_id = strategy.get("content_type_override") or editorial_category
    if not cc.get_by_id(content_type_id):
        content_type_id = cc.weighted_choice(weight_overrides)["id"]
    print(f"[calendar] content_type={content_type_id}")

    tried_content_types = set()
    for attempt in range(MAX_GENERATION_ATTEMPTS):
        # Prefer a real trend on the first attempt; fall back to evergreen (no trend) after
        candidate_trend = all_trends[attempt] if attempt < len(all_trends) else None

        idea = content_gen.generate_post(strategy, content_type_id, candidate_trend)
        if not idea:
            print(f"[main] Attempt {attempt+1}: generation failed, retrying with a different content type.")
            tried_content_types.add(content_type_id)
            content_type_id = cc.weighted_choice(weight_overrides, exclude=list(tried_content_types))["id"]
            continue

        qscore = quality_score.score_post(idea)
        print(f"[quality] total={qscore['total']}  pass={qscore['pass']}  feedback={qscore.get('feedback')}")
        if not qscore["pass"]:
            tried_content_types.add(content_type_id)
            content_type_id = cc.weighted_choice(weight_overrides, exclude=list(tried_content_types))["id"]
            continue

        if duplicate_prevention.is_duplicate(idea["headline"], idea["caption"], idea.get("trend_used")):
            print(f"[main] Attempt {attempt+1}: too similar to a recent post, retrying.")
            tried_content_types.add(content_type_id)
            content_type_id = cc.weighted_choice(weight_overrides, exclude=list(tried_content_types))["id"]
            continue

        idea["_strategy"] = strategy
        return idea

    print("[main] No post cleared quality/duplicate checks after max attempts. Skipping today by design.")
    return None


def render_and_publish(idea: dict):
    caption = idea["caption"] + "\n\n" + idea["cta"] + "\n\n" + " ".join(idea["hashtags"])
    kicker = idea["problem"].replace("_", " ")

    if idea["format"] == "single_image":
        raw_path = os.path.join(RAW_DIR, "single_raw.png")
        generate_image(idea["image_prompt"], raw_path)
        final_path = os.path.join(OUTPUT_DIR, "single.png")
        render_feed_slide(idea["headline"], raw_path, final_path, kicker=kicker)

        img_url = f"{PUBLIC_HOST_BASE}/single.png"
        result = publish_meta.post_single_image(img_url, caption)
        publish_meta.post_to_facebook_page(img_url, caption)
        post_id = result.get("id", "")

    elif idea["format"] == "carousel":
        slides = idea.get("slide_headlines") or idea.get("carousel_slides") or [idea["headline"]]
        raw_paths = generate_carousel([idea["image_prompt"]] * len(slides), RAW_DIR)
        final_paths = []
        for i, raw in enumerate(raw_paths):
            final = os.path.join(OUTPUT_DIR, f"slide_{i+1}.png")
            render_feed_slide(slides[i], raw, final, kicker=kicker if i == 0 else None,
                               show_cta=(i == len(raw_paths) - 1))
            final_paths.append(final)
        urls = [f"{PUBLIC_HOST_BASE}/{os.path.basename(p)}" for p in final_paths]
        result = publish_meta.post_carousel(urls, caption)
        post_id = result.get("id", "")

    elif idea["format"] == "reel":
        raw_paths = generate_carousel([idea["image_prompt"]] * 4, RAW_DIR)
        video_path = os.path.join(OUTPUT_DIR, "reel.mp4")
        build_reel(raw_paths, video_path, caption_lines=idea.get("slide_headlines"))
        cover_path = os.path.join(OUTPUT_DIR, "reel_cover.png")
        render_reel_cover(idea["headline"], raw_paths[0], cover_path)
        video_url = f"{PUBLIC_HOST_BASE}/reel.mp4"
        cover_url = f"{PUBLIC_HOST_BASE}/reel_cover.png"
        result = publish_meta.post_reel(video_url, caption, cover_url=cover_url)
        post_id = result.get("id", "")

    else:
        print(f"[main] Unknown format {idea['format']}, aborting publish.")
        return

    print("Published:", result)
    analytics.log_post(post_id, idea, platform="instagram")
    duplicate_prevention.record_post(idea["headline"], idea["caption"], idea.get("trend_used"))


def run():
    idea = build_todays_post()
    if not idea:
        return
    print(f"[main] Publishing content_type={idea['content_type']}  pillar={idea['pillar']}  "
          f"problem={idea['problem']}  format={idea['format']}")
    render_and_publish(idea)


if __name__ == "__main__":
    run()
