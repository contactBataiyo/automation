"""
PHASE 1 — Central source of truth for everything about Bataiyo.

Every content-generating prompt in this system (strategy_engine, content_gen,
the story engines) imports from here instead of hardcoding brand facts. If
Bataiyo's positioning changes, this is the only file that needs editing.
"""

BRAND = {
    "name": "Bataiyo",
    "tagline": "Bharosa Apno Ka",
    "mission": (
        "To digitize word-of-mouth so that trust, not advertising budgets, "
        "decides who gets discovered — for services, jobs, and marriages."
    ),
    "vision": (
        "A India where every recommendation — for a plumber, a job referral, "
        "or a marriage introduction — comes from someone who actually knows, "
        "not a paid listing or a fake star rating."
    ),
    "positioning": (
        "India's digital word-of-mouth network — not a service marketplace. "
        "Bataiyo helps people discover trusted services, jobs, and marriage "
        "connections through real human recommendations, with zero commission "
        "for providers, forever."
    ),
    "tone": (
        "Warm, trustworthy, conversational, slightly desi (Hindi-English mix "
        "welcome — 'bharosa', 'apno ka'). Speaks like a helpful neighbour, "
        "never a salesperson. Confident but never hard-sell. Educates before "
        "it asks for anything."
    ),
}

# PHASE 1 — Pillars: the categories of trust Bataiyo operates in. Every post
# should map to one (content_gen enforces this).
PILLARS = {
    "trusted_recommendations": {
        "label": "Trusted Recommendations",
        "description": "The core mechanic — recommendations from people you actually know, replacing ads and star ratings.",
    },
    "services": {
        "label": "Services",
        "description": "Finding reliable local service providers (home repair, tutoring, beauty, events, etc.) through your network.",
    },
    "jobs": {
        "label": "Jobs",
        "description": "Referral-based hiring and job discovery — people vouching for people, not just resumes.",
    },
    "marriage": {
        "label": "Marriage",
        "description": "Introductions and matchmaking rooted in trusted family/community networks, not algorithms.",
    },
    "communities": {
        "label": "Communities",
        "description": "Neighbourhood, alumni, and interest communities that are the actual source of trust Bataiyo digitizes.",
    },
}

# PHASE 1 — Principles: things Bataiyo stands FOR and AGAINST. Useful for
# generating "founder opinion" / "trust tip" style content with real teeth.
PRINCIPLES = [
    {"id": "trust_over_ratings", "statement": "Trust over ratings — a recommendation from someone you know beats a 5-star average from strangers."},
    {"id": "no_fake_reviews", "statement": "No fake reviews — Bataiyo has no review/rating system to game in the first place."},
    {"id": "zero_commission", "statement": "Zero commission for providers, forever — no cut taken from anyone's earnings."},
    {"id": "people_over_algorithms", "statement": "People over algorithms — your feed of recommendations comes from your network, not a ranking model."},
    {"id": "community_first", "statement": "Community first — the app exists to strengthen real-world word of mouth, not replace it."},
    {"id": "no_ads", "statement": "No paid ads or boosted listings — visibility is earned through genuine recommendations only."},
    {"id": "real_recommendations", "statement": "Real recommendations from real relationships — not incentivized or bought."},
    {"id": "word_of_mouth", "statement": "Word of mouth is the oldest trust mechanism there is — Bataiyo just makes it searchable."},
    {"id": "authenticity", "statement": "Authenticity over virality — the goal is a good recommendation, not a viral post."},
]

# PHASE 1 — Expanded problem list (~20). Every post traces back to exactly
# one of these. `pillar` links each problem to a PILLARS key above.
PROBLEMS = [
    {"id": "trusted_electricians", "pillar": "services", "problem": "Finding a trustworthy electrician/plumber/technician on short notice is genuinely stressful.", "bataiyo_angle": "Your network already knows a good one — Bataiyo surfaces that instead of a stranger's listing."},
    {"id": "trusted_tutors", "pillar": "services", "problem": "Parents struggle to find tutors who are actually good, not just well-reviewed.", "bataiyo_angle": "Recommendations come from parents who've actually seen results, not paid listings."},
    {"id": "trusted_doctors", "pillar": "services", "problem": "Choosing a doctor/clinic from Google reviews alone is a gamble — reviews are gameable.", "bataiyo_angle": "A recommendation from someone in your circle who's actually been treated carries more weight than star ratings."},
    {"id": "wedding_vendors", "pillar": "marriage", "problem": "Finding reliable wedding vendors (caterers, photographers, decorators) under time pressure is chaotic.", "bataiyo_angle": "Bataiyo taps the collective experience of your community's recent weddings instead of cold-searching."},
    {"id": "finding_jobs", "pillar": "jobs", "problem": "Most job discovery is still resume-into-a-black-hole, disconnected from any real vouching.", "bataiyo_angle": "Bataiyo's job discovery runs on referrals from people who know your work, not just keyword-matched resumes."},
    {"id": "getting_referrals", "pillar": "jobs", "problem": "Asking for a referral feels awkward, so many people just don't, and miss real opportunities.", "bataiyo_angle": "Bataiyo makes referrals a normal, structured part of how opportunities move through your network."},
    {"id": "growing_local_business", "pillar": "services", "problem": "Small/local businesses can rarely afford ads, so visibility goes to whoever pays most, not who's best.", "bataiyo_angle": "Bataiyo gets good providers discovered through word of mouth, at zero cost to them."},
    {"id": "marriage_introductions", "pillar": "marriage", "problem": "Matchmaking through apps often feels transactional and disconnected from real family/community trust.", "bataiyo_angle": "Bataiyo roots introductions in the trust networks families already have, digitized."},
    {"id": "community_recommendations", "pillar": "communities", "problem": "Good local knowledge (best doctor, safest neighbourhood, reliable POC) rarely leaves a WhatsApp group.", "bataiyo_angle": "Bataiyo turns scattered community knowledge into something searchable and lasting."},
    {"id": "paid_ads_distrust", "pillar": "trusted_recommendations", "problem": "People increasingly distrust anything that's clearly a paid ad or boosted listing.", "bataiyo_angle": "Bataiyo has no ads to distrust — every recommendation is organic by design."},
    {"id": "fake_reviews", "pillar": "trusted_recommendations", "problem": "Online reviews are widely known to be gamed — paid, incentivized, or outright fake.", "bataiyo_angle": "Bataiyo skips the star-rating system entirely and relies on real people you know."},
    {"id": "hidden_commissions", "pillar": "services", "problem": "Most service platforms take a 20-30% commission, which quietly inflates prices for everyone.", "bataiyo_angle": "Bataiyo takes zero commission — providers keep 100% of what they earn."},
    {"id": "local_discovery", "pillar": "services", "problem": "Discovering what's actually good nearby (not just what ranks well on Google/Maps) is harder than it should be.", "bataiyo_angle": "Bataiyo surfaces what your own network rates highly, not what's paid for placement."},
    {"id": "recommendation_fatigue", "pillar": "trusted_recommendations", "problem": "People are tired of asking the same 'does anyone know a good X' question in five different WhatsApp groups.", "bataiyo_angle": "Bataiyo centralizes that ask so your network's collective knowledge is one search away."},
    {"id": "information_overload", "pillar": "trusted_recommendations", "problem": "Too many options and too many conflicting reviews make simple decisions exhausting.", "bataiyo_angle": "Bataiyo narrows the field to what people you trust actually recommend."},
    {"id": "trust_issues_strangers", "pillar": "services", "problem": "Letting an unverified stranger into your home for a repair or service is a real trust leap.", "bataiyo_angle": "A Bataiyo recommendation means someone you know has already taken that leap and vouched for the outcome."},
    {"id": "quality_uncertainty", "pillar": "services", "problem": "You often can't tell if a service will be good until it's too late and you've already paid.", "bataiyo_angle": "A recommendation from someone with nothing to gain is the closest thing to a guarantee you'll get."},
    {"id": "neighbourhood_services", "pillar": "communities", "problem": "Neighbourhood-specific needs (a good cook, a reliable driver, a nearby tutor) rarely have good discovery tools.", "bataiyo_angle": "Bataiyo is built around exactly this kind of hyperlocal, network-based discovery."},
    {"id": "home_maintenance", "pillar": "services", "problem": "Home maintenance issues (leaks, wiring, appliances) often need someone reliable fast, with no time to vet options.", "bataiyo_angle": "Your network's go-to providers are a search away, no vetting from scratch needed."},
    {"id": "emergency_contacts", "pillar": "communities", "problem": "In a genuine emergency, generic search results are the worst possible source of a service provider.", "bataiyo_angle": "Bataiyo's core promise — trusted people, not random listings — matters most exactly when it's urgent."},
]

# PHASE 1 — Audience definitions
AUDIENCES = {
    "homeowners": "People managing a household — need reliable home services, often under time pressure.",
    "students": "Students/young adults — need tutors, local know-how, first job/internship referrals.",
    "parents": "Parents — need tutors, doctors, childcare, school community knowledge.",
    "professionals": "Working professionals — care about job referrals, networking, career mobility.",
    "businesses": "Small/local business owners — need visibility and customer discovery without ad spend.",
    "providers": "Service providers (electricians, tutors, etc.) — care about earning fairly and getting discovered.",
}

# PHASE 1 — Reusable CTA library, grouped by the goal it serves (used by
# strategy_engine to pick a CTA that matches today's objective).
CTA_LIBRARY = {
    "increase_downloads": [
        "Download Bataiyo and see what your network already knows.",
        "Your next recommendation is already in your network. Get Bataiyo.",
    ],
    "educate": [
        "Learn how word-of-mouth, digitized, actually works — link in bio.",
        "Curious how this works? We break it down in the app.",
    ],
    "build_trust": [
        "No ads. No fake reviews. Just people you trust. That's Bataiyo.",
        "See why real recommendations beat star ratings — try Bataiyo.",
    ],
    "increase_referrals": [
        "Know someone who needs this? Tag them.",
        "Share this with the one friend who always knows a guy.",
    ],
    "help_providers": [
        "Are you a service provider? Join Bataiyo and keep 100% of what you earn.",
        "Zero commission, forever. Providers, this one's for you.",
    ],
    "engagement": [
        "Tell us in the comments — who's your most-recommended person?",
        "Drop a 🙌 if you've ever found a great provider through a friend.",
    ],
}

HASHTAGS_BASE = ["#Bataiyo", "#BharosaApnoKa", "#ZeroCommission", "#WordOfMouth", "#TrustedRecommendations"]


def get_problem(problem_id: str) -> dict:
    return next((p for p in PROBLEMS if p["id"] == problem_id), None)


def get_pillar_for_problem(problem_id: str) -> str:
    p = get_problem(problem_id)
    return p["pillar"] if p else None
