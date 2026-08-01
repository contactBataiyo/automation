"""
Central brand config. Every content-generation call pulls from here,
so tone/positioning stays consistent no matter what trend triggered the post.
"""

BRAND_KIT = {
    # CONFIRMED from bataiyo.com's theme-color meta tag — do not change without checking site.
    "primary_blue": "#1570EF",

    # Suggested companion palette (NOT confirmed from official brand assets — replace
    # with exact hex codes from Bataiyo's brand guidelines/logo files if you have them).
    "navy_text": "#0B2545",       # dark text / high-contrast backgrounds
    "background": "#F7F9FC",      # light neutral background
    "trust_green": "#12B76A",     # "zero commission" / checkmark / trust cues
    "accent_amber": "#FDB022",    # sparing use — CTA highlight only, not a primary color

    # Fonts confirmed available in this environment (Poppins reads as modern/trustworthy,
    # a common choice for Indian fintech/consumer apps — swap if Bataiyo's actual
    # brand font differs).
    "font_bold": "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf",
    "font_semibold": "/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf",
    "font_regular": "/usr/share/fonts/truetype/google-fonts/Poppins-Regular.ttf",

    "logo_wordmark": "Bataiyo",     # placeholder text-logo until you supply a real .png logo
    "kicker_tagline": "BHAROSA APNO KA",
}

# The specific, real problems Bataiyo solves. Every post must trace back to
# ONE of these — this is what stops trend-jacking from turning into generic
# "look, we noticed a trend too" filler content.
PROBLEMS_SOLVED = [
    {
        "id": "fake_reviews",
        "problem": "You can't trust online reviews anymore — many are fake, paid, or bot-generated.",
        "bataiyo_angle": "Bataiyo replaces star ratings with recommendations from people in your own network who've actually used the service.",
    },
    {
        "id": "commission_squeeze",
        "problem": "Service providers on most apps lose 20-30% of every job to platform commission, so prices creep up for everyone.",
        "bataiyo_angle": "Bataiyo charges zero commission, forever — providers keep 100% of what they earn.",
    },
    {
        "id": "stranger_risk",
        "problem": "Letting an unknown, unverified person into your home (electrician, cleaner, tutor) is a real trust leap.",
        "bataiyo_angle": "Bataiyo surfaces people your own circle already vouches for, so it's never a total stranger.",
    },
    {
        "id": "middleman_markup",
        "problem": "Layers of agents/middlemen between you and a service provider quietly inflate the price.",
        "bataiyo_angle": "Bataiyo connects you directly through your network — no middleman markup.",
    },
    {
        "id": "small_business_visibility",
        "problem": "Skilled local providers (tutors, artisans, technicians) struggle to get discovered without paying for ads or listings.",
        "bataiyo_angle": "Bataiyo gets small/local providers discovered through genuine word of mouth, not ad spend they can't afford.",
    },
]

BRAND = {
    "name": "Bataiyo",
    "tagline": "Bharosa Apno Ka",
    "positioning": (
        "India's first zero-commission digital word-of-mouth app. "
        "Connects users to trusted service providers (plumbers, tutors, "
        "electricians, beauty, home repair, and 250+ categories) through "
        "their own personal network — friends, family, acquaintances — "
        "instead of fake reviews or paid ads. Service providers keep 100% "
        "of earnings, forever."
    ),
    "voice": (
        "Warm, trustworthy, slightly desi-conversational (Hindi-English mix "
        "is fine, e.g. 'bharosa', 'apno ka'). Never salesy or corporate. "
        "Speaks like a helpful neighbour, not an ad. Confident about zero "
        "commission as the core differentiator vs. Urban Company / JustDial-style apps."
    ),
    "audience": [
        "Urban + semi-urban Indians looking for trustworthy local services",
        "Service providers (plumbers, tutors, salons, electricians etc.) tired of commission cuts",
    ],
    "core_themes": [
        "zero commission, forever",
        "trust > ads/reviews",
        "word of mouth, digitized",
        "supporting local/small service businesses",
        "no fake reviews, no middlemen",
    ],
    "hashtags_base": [
        "#Bataiyo", "#BharosaApnoKa", "#ZeroCommission",
        "#WordOfMouth", "#TrustedServices", "#MadeInIndia",
    ],
    "handles": {
        "instagram": "@bataiyo.official",
        "facebook": "bataiyo.official",
        "linkedin": "bataiyo",
    },
}

# Content mix — used by main.py to decide what to produce for a given trend
CONTENT_FORMATS = ["single_image", "carousel", "reel"]
