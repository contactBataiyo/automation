# Setup Guide (detailed, step-by-step)

Do these in order. Steps 1 and 3 involve waiting on someone else (Google is
instant, LinkedIn is a queue) — start step 3 today even if you finish 1, 2,
4 first, so it's not the thing blocking you later.

---

## Step 1 — Gemini API key (5 minutes, instant)

1. Go to https://aistudio.google.com/app/apikey
2. Sign in with any Google account.
3. Click **Create API key** → choose "Create key in new project" if you
   don't have one already.
4. Copy the key (starts with `AIza...`). This is your `GEMINI_API_KEY`.
5. Free tier is per-model, per-day request limits — a few posts/day across
   trend-filtering + caption-writing calls stays comfortably inside it. If
   you ever see a `429` quota error, it resets daily; no card needed.

---

## Step 2 — Meta Graph API (Instagram + Facebook) — 30–45 minutes, instant approval for your own accounts

**2a. Prep your accounts**
1. Open Instagram app → Settings → Account type → switch to **Professional
   account** → **Business** (Creator also works, Business is more reliable
   for the Graph API).
2. Link it to a **Facebook Page** you manage (Instagram Settings → Linked
   Accounts → Facebook). If you don't have a Bataiyo Facebook Page yet,
   create one first at facebook.com/pages/create.

**2b. Create the developer app**
1. Go to https://developers.facebook.com/apps → **Create App**.
2. Choose app type **"Other"** → **"Business"**.
3. Name it something like `Bataiyo Content Bot`.
4. In the app dashboard, click **Add Product** → find **Instagram Graph
   API** → **Set Up**.

**2c. Add yourself as a tester (this is what skips App Review)**
1. In the app dashboard sidebar: **App Roles** → **Roles**.
2. Add your own Facebook account as an **Administrator** (you probably
   already are, since you created the app).
3. Under **App Roles → Instagram Testers**, add your Instagram Business
   account and accept the invite from inside the Instagram app
   (Settings → Apps and Websites → Tester Invites).
4. Because you're only publishing to accounts you personally administer,
   Meta lets this work in **Development Mode** — you do NOT need to submit
   for public App Review. This is the single biggest thing that makes this
   free-and-fast instead of free-and-slow.

**2d. Get IDs and a long-lived token**
1. Go to **Graph API Explorer**: https://developers.facebook.com/tools/explorer/
2. Select your app from the dropdown.
3. Click **Generate Access Token**, and when prompted, grant these
   permissions: `instagram_basic`, `instagram_content_publish`,
   `pages_show_list`, `pages_read_engagement`, `pages_manage_posts`.
4. Run a test query: `GET /me/accounts` → find your Page → copy its `id`.
   This is your `FB_PAGE_ID`.
5. Run: `GET /{FB_PAGE_ID}?fields=instagram_business_account` → copy the
   returned ID. This is your `IG_BUSINESS_ACCOUNT_ID`.
6. The token from Graph API Explorer is short-lived (~1 hour). Exchange it
   for a long-lived one (60 days, renewable):
   ```
   GET /oauth/access_token?grant_type=fb_exchange_token
       &client_id={APP_ID}&client_secret={APP_SECRET}
       &fb_exchange_token={SHORT_LIVED_TOKEN}
   ```
   Find `APP_ID`/`APP_SECRET` in **App Settings → Basic**.
7. This long-lived token is your `META_PAGE_ACCESS_TOKEN`. It expires every
   ~60 days — set a calendar reminder to regenerate it (or automate the
   refresh call, it's the same request, just re-run periodically).

---

## Step 3 — LinkedIn Company Page API — start early, this is the slow one

1. Go to https://www.linkedin.com/developers/apps → **Create app**.
2. Link it to Bataiyo's LinkedIn **Company Page** (you must be a page admin).
3. Under **Products**, request **"Share on LinkedIn"** (usually auto-approved,
   gives basic posting) AND apply for **"Marketing Developer Platform"**
   access if you want full organization posting control — this one goes
   through LinkedIn's review team. Fill in the use-case form honestly: "own
   brand's content automation," not a third-party tool.
4. Approval timelines vary — anywhere from a few days to a few weeks.
   There's no way to speed this up; it's a manual review queue on
   LinkedIn's side, not a technical blocker on yours.
5. Once approved: **Auth** tab → generate an access token with scopes
   `w_organization_social` and `r_organization_social`.
6. Find your Company Page's numeric ID: visible in the Page's admin URL
   (linkedin.com/company/**12345678**/admin/) — this is `LINKEDIN_ORG_ID`.
7. The token is `LINKEDIN_ACCESS_TOKEN`.

**While you wait:** if you want *any* LinkedIn automation live sooner,
`w_member_social` (personal profile posting) only needs basic "Sign In with
LinkedIn," which is instant — you could post from a founder's personal
profile in the meantime instead of the Company Page.

---

## Step 4 — Hosting generated media (10 minutes)

The Graph API needs a **public URL** for every image/video it posts — it
can't accept a raw file upload from GitHub Actions directly.

Easiest free option — GitHub Pages on this same repo:
1. Push this project to a GitHub repo (can be public or private + Pages
   works on public repos for free; private repo Pages needs GitHub Pro).
   If you want it private, use Cloudflare Pages or Netlify's free tier
   instead — same idea, different button.
2. Repo → **Settings → Pages** → Source: **Deploy from branch** → branch
   `main`, folder `/output` (or `/ (root)` if you restructure).
3. Your public base URL will be `https://YOUR_USERNAME.github.io/REPO_NAME`.
4. Set this as the `PUBLIC_HOST_BASE` secret/env var.

Note the `.github/workflows/daily_post.yml` already commits generated
`output/` files back to the repo after each run, so Pages picks up new
media automatically.

---

## Step 5 — Add secrets to GitHub (5 minutes)

Repo → **Settings → Secrets and variables → Actions → New repository secret**.
Add each of these (names must match exactly, `daily_post.yml` reads them):

```
GEMINI_API_KEY
IG_BUSINESS_ACCOUNT_ID
FB_PAGE_ID
META_PAGE_ACCESS_TOKEN
LINKEDIN_ORG_ID
LINKEDIN_ACCESS_TOKEN
PUBLIC_HOST_BASE
```

---

## Step 6 — Test locally before trusting the cron job

```bash
pip install -r requirements.txt
sudo apt-get install ffmpeg   # if not already installed

export GEMINI_API_KEY=...
export IG_BUSINESS_ACCOUNT_ID=...
export FB_PAGE_ID=...
export META_PAGE_ACCESS_TOKEN=...
export LINKEDIN_ORG_ID=...
export LINKEDIN_ACCESS_TOKEN=...
export PUBLIC_HOST_BASE=https://your-username.github.io/your-repo

python main.py
```

Watch the console output — it prints which trend it picked, which
`problem_id` it mapped to, and its `reasoning`, before it publishes
anything. If it says "no trend had a genuine connection," that's the
skip-logic working as designed, not a bug — run it again another day or
lower the bar slightly in `content_gen.py` if it's skipping too often.

---

## Step 8 — (v2) Wire up the analytics feedback loop

The learning engine only works once `analytics.py` has real engagement
numbers to read, which means a **second**, separately-scheduled job:

```bash
python3 -c "
import analytics, os
analytics.fetch_and_update_insights(
    os.environ['IG_BUSINESS_ACCOUNT_ID'],
    os.environ['META_PAGE_ACCESS_TOKEN'],
)
"
```

Run this once/day (a second GitHub Actions workflow on its own cron, e.g.
06:00 UTC, covering the previous day's posts — Instagram insights aren't
reliable until a post has had ~24h). Once `analytics/posts.csv` has a few
weeks of data with `engagement_rate` filled in, `learning.py` automatically
starts biasing `content_categories.py`'s weights and feeding signals into
`strategy_engine.py` — no code changes needed, it activates on its own once
there's enough data (`MIN_SAMPLES = 3` per group, in `learning.py`).

---

## Step 9 — Turn on the daily content cron job

Once a local test run of `python main.py` works end to end, the GitHub
Actions workflow will run automatically on its schedule
(`.github/workflows/daily_post.yml`, default 10:00 IST daily). You can also
trigger it manually anytime from the repo's **Actions** tab → select the
workflow → **Run workflow**.
