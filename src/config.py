"""Configuration for NIH Grant Scraper."""

import os
from dotenv import load_dotenv

load_dotenv()

# Research keywords based on your bibliography
KEYWORDS = [
    # Core areas
    "aging", "cardiovascular", "atherosclerosis", "immunology",
    # T cell immunology
    "T cell", "CD8", "memory T cell", "clonal expansion",
    # Cardiovascular/vascular
    "aortic", "vascular", "cardiac", "inflammation",
    # Methods/techniques
    "flow cytometry", "spectral flow", "single-cell", "proteomics",
    "high-dimensional", "proteome"
]

# NIH Reporter API settings
NIH_REPORTER_API_URL = "https://api.reporter.nih.gov/v2/projects/search"
ACTIVITY_CODES = ["R01"]
DAYS_LOOKBACK = 7

# Priority study sections (get +9 relevance score)
PRIORITY_STUDY_SECTIONS = ["AVI", "CDIN", "CMAD", "CMBG", "CMND", "BINP"]

# Minimum relevance score to include in email
MIN_RELEVANCE_SCORE = 5

# NIH Guide RSS Feed
NIH_GUIDE_RSS_URL = "https://grants.nih.gov/grants/guide/newsfeed/fundingopps.xml"

# Email settings (loaded from environment)
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT")
