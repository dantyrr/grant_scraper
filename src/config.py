"""Configuration for NIH Grant Scraper."""

import os
from dotenv import load_dotenv

load_dotenv()

# Research keywords based on your bibliography
KEYWORDS = [
    # Core areas
    "aging", "mitochondria", "mitochondrial", "immunology",
    "cardiovascular", "atherosclerosis", "neuroinflammation",
    # Specific topics
    "bioenergetics", "respirometry", "T cell", "CD8",
    "microglia", "inflammation", "oxidative stress",
    "cardiac", "vascular", "senescence"
]

# NIH Reporter API settings
NIH_REPORTER_API_URL = "https://api.reporter.nih.gov/v2/projects/search"
ACTIVITY_CODES = ["R01"]
DAYS_LOOKBACK = 7

# NIH Guide RSS Feed
NIH_GUIDE_RSS_URL = "https://grants.nih.gov/grants/guide/newsfeed/fundingopps.xml"

# Email settings (loaded from environment)
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT")
