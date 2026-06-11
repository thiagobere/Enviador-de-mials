"""Configuration for Thiago Berenstein's Sponsor Bot."""

# --- Pilot Profile ---
PILOT_NAME = "Thiago Berenstein"
PILOT_EMAIL = "thi2012x@gmail.com"
PILOT_IG_FOLLOWERS = "4K"
PILOT_MONTHLY_VIEWS = "1.5M"
PILOT_SPORT = "karting"
PILOT_COUNTRY = "Argentina"
PILOT_DESCRIPTION = (
    "karting pilot, engineering student, and content creator from Argentina. "
    "I compete in karting championships and create content on Instagram and YouTube "
    f"covering motorsport, karting, and real racing, reaching up to {PILOT_MONTHLY_VIEWS} "
    f"monthly views with {PILOT_IG_FOLLOWERS} Instagram followers."
)

# --- Gmail Label ---
# Label ID created for threads the bot should monitor and respond to
BOT_LABEL_ID = "Label_55"
BOT_LABEL_NAME = "Sponsor/🤖 Bot-Activo"

# --- Outreach limits ---
COMPANIES_PER_DAY = 100
MAX_FOLLOW_UPS = 2

# --- Company categories to target ---
SEARCH_CATEGORIES = [
    # Karting & motorsport
    "karting helmet brands sponsorship",
    "karting suit manufacturer sponsorship racing",
    "karting chassis brand sponsorship",
    "karting gloves boots racing gear brand",
    "motorsport apparel brand sponsorship",
    "kart racing tire brand sponsorship",
    "karting accessory brand",
    # Energy & nutrition
    "energy drink brand sponsorship Argentina",
    "sports nutrition supplement brand sponsorship",
    "hydration sports drink brand sponsorship",
    # Tech & gaming
    "gaming peripheral brand sponsorship content creator",
    "sim racing hardware brand sponsorship",
    "esports hardware brand sponsorship",
    "tech gadget brand creator sponsorship",
    # Automotive
    "automotive parts brand motorsport sponsorship",
    "car care product brand racing sponsorship",
    "tire brand motorsport sponsorship",
    "lubricant oil brand motorsport sponsorship",
    # Lifestyle & apparel
    "sports apparel brand ambassador motorsport",
    "racing lifestyle brand ambassador Argentina",
    "sunglasses brand motorsport sponsorship",
    "watch brand motorsport ambassador",
    # Argentine / Latin American brands
    "marca argentina deportiva sponsorship",
    "empresa argentina sponsorship piloto",
    "marca latinoamericana sponsorship motorsport",
    # Financial / Fintech
    "fintech app brand ambassador Argentina",
    "crypto exchange brand ambassador sports",
    # Tools / Engineering
    "engineering software sponsorship student",
    "3D printing brand sponsorship creator",
]

# --- Email subject template ---
EMAIL_SUBJECT_TEMPLATE = "Sponsorship Partnership – Karting Pilot & Content Creator | {company}"

# --- Calendar settings ---
DEFAULT_MEETING_DURATION_MINUTES = 30
DEFAULT_MEETING_HOUR = 10  # 10 AM
TIMEZONE = "America/Argentina/Buenos_Aires"
