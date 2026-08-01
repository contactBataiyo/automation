# What you can change

Everything here is a small, contained edit — no architecture changes needed.

## Brand & visuals (`config.py`, `template_render.py`)

- **Exact colors**: only `primary_blue` is confirmed from your live site.
  If you have an official brand kit, replace `navy_text`, `background`,
  `trust_green`, `accent_amber` with the real values in `BRAND_KIT`.
- **Real logo instead of text wordmark**: currently `logo_wordmark` just
  draws "Bataiyo" as text. Swap this for an actual `.png` logo by editing
  `template_render.py`'s two spots that call `draw.text(..., BRAND_KIT["logo_wordmark"])`
  — replace with `canvas.paste(logo_img, (x, y), logo_img)` using your logo file.
- **Fonts**: `font_bold`/`font_semibold`/`font_regular` point at Poppins,
  which is a reasonable default but not confirmed as Bataiyo's actual
  brand typeface. Any `.ttf`/`.otf` file works — point the paths at it.
- **Layout**: card proportions, illustration panel size, footer CTA style —
  all plain Pillow drawing calls in `template_render.py`, easy to nudge.
- **Devanagari/Hindi text**: no Devanagari font is currently installed in
  this environment. If you want actual Hindi script (not just transliterated
  "Bharosa Apno Ka") on images, install a font like Noto Sans Devanagari
  and point `font_bold` etc. at it for Hindi-text elements specifically.

## Content strategy (`config.py`'s `PROBLEMS_SOLVED`)

- **Add/edit problems**: if Bataiyo's positioning shifts (new service
  categories, a new differentiator), add an entry here. Every future post
  automatically has access to it as a valid angle.
- **Remove a problem**: if one isn't resonating, delete it — the model can
  no longer use it, no prompt-tuning needed elsewhere.
- **Tighten or loosen the "genuine bridge" bar**: `content_gen.py`'s
  `SYSTEM_CONTEXT` rule #3 is what makes it skip weak trends. If it's
  skipping too often, soften the wording ("a reasonably clever bridge" vs.
  "genuinely clever"); if posts still feel forced, tighten it further.

## Human oversight

- Right now `main.py` publishes automatically once content is generated.
  If you want a review step: add a Slack/Telegram webhook call before the
  `publish_meta.post_*` lines that sends the caption + rendered image and
  waits for a thumbs-up/down before proceeding. This is a ~20-line addition,
  I can build it if you want it.
- Alternative middle ground: keep it fully automatic but log every decision
  (trend, problem_id, reasoning, caption) to a file/sheet so you can audit a
  week's worth of posts at a glance rather than approving one by one.

## Posting cadence & format mix

- `daily_post.yml`'s cron currently runs once/day. Change the cron
  expression for multiple times/day, or different days for different
  platforms.
- `main.py`'s `pick_best_trend` currently checks up to 8 trends and stops
  at the first relevant one — you could instead score all candidates and
  pick the strongest, or generate 2–3 posts per run for a content queue
  instead of same-day publishing.
- Format mix (single image vs. carousel vs. reel) is currently the model's
  choice per-post. You could instead force a fixed weekly rhythm (e.g.
  reel on Mon/Thu, carousel on Wed, single image otherwise) by passing a
  suggested format into the `content_gen` prompt.

## Trend sources (`trends.py`)

- Currently Google Trends India + 2 subreddits. Easy additions: Twitter/X's
  free API tier, Google News RSS feeds for specific categories (home
  services, gig economy, consumer trust), or industry-specific subreddits.
- You could also weight sources — e.g. treat r/smallbusiness hits as
  more likely to map to the `commission_squeeze` problem specifically,
  and pass that hint along to `content_gen.py`.

## Image quality

- Pollinations.ai (current default) is free and unlimited but not
  agency-grade. `image_gen.py` is a single, isolated file — swapping in a
  different model (paid or a different free tier) only touches that file,
  nothing downstream changes since `template_render.py` treats the output
  as "just an illustration to crop into the template" either way.

## What I'd genuinely leave alone for now

The problem-first gating in `content_gen.py` and the template-based brand
enforcement in `template_render.py` are the two things doing the most work
to keep this from turning into generic trend-jacking content — I'd treat
those as the foundation and tune around them rather than loosening them
for the sake of posting more often.
