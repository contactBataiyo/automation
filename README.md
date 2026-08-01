# Bataiyo Trend-to-Post Automation

A $0-cost pipeline: trending topic → on-brand caption → generated image/carousel/reel → auto-published to Instagram, Facebook, LinkedIn.

# Bataiyo AI Marketing Manager (v2)

Not a caption generator anymore — a pipeline that decides *what today's post
should accomplish* before it writes a single word, then generates, scores,
checks for duplicates, brands, and publishes it. Still $0 to run.

## Architecture

```
strategy_engine.py     "If you were Head of Marketing, what should today's
                         post accomplish?" — picks ONE objective before any
                         content exists (increase_downloads / educate /
                         build_trust / increase_referrals / support_providers
                         / celebrate_moment / community_story / engagement)
        v
editorial_calendar.py   Today's default content category by weekday
        v
content_categories.py   Weighted content-type rotation (biased over time by
                         learning.py's performance data)
        v
trends.py               Google Trends + Reddit + Google News RSS + festival
                         calendar, scored and deduplicated
        v
content_gen.py           Knowledge-base-driven generation, routes to a
                         specialist story engine or generic generation
        v
quality_score.py        Self-scores against a rubric, rejects <80/100
        v
duplicate_prevention.py  Blocks near-identical posts within 60 days
        v
image_gen -> template_render -> video_gen      UNCHANGED from v1
        v
publish_meta / publish_linkedin                 UNCHANGED from v1
        v
analytics.py + learning.py       Logs performance, feeds back into
                                   content_categories' weights next run
```

`knowledge_base.py` sits underneath all of this — brand mission, pillars,
~20 real problems, audiences, and a CTA library. Every prompt in the system
imports from it instead of hardcoding brand facts.

Note: `config.py` (from v1) still exists separately and still holds
`BRAND_KIT` — the *visual* brand config (colors, fonts, logo) that
`template_render.py` and `video_gen.py` use. That split is intentional:
`knowledge_base.py` is what the *writing* prompts import, `config.py` is
what the *rendering* code imports. Untouched per the spec's instruction not
to rewrite the rendering pipeline.

Specialist story engines (each a thin, focused generator): `recommendation_story.py`,
`before_internet.py`, `community_story.py`, `job_story.py`, `marriage_story.py`.

## What's fully built vs. lighter-weight

**Fully built, working end to end:** knowledge_base, content_gen (rewrite),
content_categories, editorial_calendar, strategy_engine, trends (expanded),
the 5 story engines, analytics, learning, duplicate_prevention, quality_score,
main.py orchestrator.

**Deliberately kept light** (per the spec's own priority ranking — these
were ⭐⭐⭐ or below):
- **Image prompt themes / reel styles** (spec phases 13–14): `template_render.py`
  and `video_gen.py` are untouched as instructed. The *variety* now comes
  from `content_gen.py` producing different `image_prompt`/`slide_headlines`
  per content type — I didn't add named reel "styles" as separate code paths,
  since that would mean touching the FFmpeg pipeline the spec says to keep.
  If you want distinct visual treatments per story type (e.g. a literal
  "Before Internet" split-panel look), that's a `template_render.py` change
  I'd do as a follow-up, not bundled into this pass.
- **Analytics storage**: CSV, as the spec explicitly allows for v1 ("later:
  SQLite"). Swapping later only touches `analytics.py`'s read/write functions.

See `SETUP.md` for setup and `CUSTOMIZE.md` for what's easy to tune.

## What's actually free vs. what needs patience

| Piece | Cost | Catch |
|---|---|---|
| Trend data (incl. Google News RSS) | Free | None |
| Gemini calls (strategy, content, quality score) | Free tier | More calls/post now (strategy + problem-pick + generation + scoring) — still well within free daily quota for a few posts/day, see SETUP.md |
| Images | Free | Quality is "good enough for social," not agency-grade |
| Video assembly | Free (ffmpeg) | No API access to IG's licensed trending sounds |
| IG/FB posting | Free | One-time dev app setup |
| LinkedIn posting | Free | MDP approval queue (days–weeks) |
| Analytics | Free | CSV-based; insights fetch needs a second scheduled run ~24h after publish |
| Hosting | Free | GitHub Pages / Actions minutes |

## Setup (one-time)

Full step-by-step walkthrough with exact click-paths: see **[SETUP.md](SETUP.md)**.
Quick summary:

1. **Gemini API key (free, instant)** — https://aistudio.google.com/app/apikey
2. **Meta Graph API (free, instant for your own accounts)** — convert your IG
   to Business/Creator, link a FB Page, create a dev app, add yourself as a
   tester (skips App Review), generate a long-lived Page Access Token.
3. **LinkedIn API (free, but a review queue)** — create an app, apply for
   Marketing Developer Platform access. Start this one first, it's slowest.
4. **Image/video hosting** — GitHub Pages on this repo (free) works well
   since the workflow already commits `output/` back automatically.
5. Add all keys as **GitHub repo secrets**.
6. Test locally, then let the GitHub Actions cron take over.

## What's actually free vs. what needs patience

| Piece | Cost | Catch |
|---|---|---|
| Trend data | Free | None |
| Gemini captions | Free tier | Daily quota — fine for a few posts/day |
| Images | Free | Quality is "good enough for social," not agency-grade |
| Video assembly | Free (ffmpeg) | No access to IG's licensed trending *sounds* via API — see `video_gen.py` note |
| IG/FB posting | Free | One-time dev app setup |
| LinkedIn posting | Free | MDP approval queue (days–weeks), not instant |
| Hosting | Free | GitHub Pages / Actions minutes have generous free limits |

## The one thing to keep manual (for now)

Instagram's actual trending-audio library isn't exposed through the API —
only the IG app has it. If matching literally-trending sounds matters to you,
the pragmatic move is: let this pipeline auto-generate the reel + caption,
then spend ~30 seconds in the IG app swapping in a trending sound before
you tap post. Everything else can run headless.

## Extending it

Full list with specifics: see **[CUSTOMIZE.md](CUSTOMIZE.md)**. Highlights:

- Swap Pollinations for a nicer image model whenever budget allows —
  isolated to `image_gen.py`, nothing downstream changes.
- Add a Slack/Telegram approval step before publish if you don't want fully
  blind auto-posting.
- Add/edit `PROBLEMS_SOLVED` in `config.py` as Bataiyo's positioning evolves.
- Swap in your real logo file and confirmed secondary brand colors as soon
  as you have them — one edit in `config.py`/`template_render.py`.
