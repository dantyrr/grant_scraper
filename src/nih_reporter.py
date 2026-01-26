"""NIH Reporter API client for fetching new R01 awards."""

import requests
from datetime import datetime, timedelta
from typing import Optional

from .config import (
    NIH_REPORTER_API_URL,
    ACTIVITY_CODES,
    DAYS_LOOKBACK,
    KEYWORDS,
    PRIORITY_STUDY_SECTIONS,
    MIN_RELEVANCE_SCORE
)


def get_date_range(days_back: int = DAYS_LOOKBACK) -> tuple[str, str]:
    """Calculate date range for the query (last N days)."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")


def build_search_query(keywords: list[str] = KEYWORDS) -> dict:
    """Build the NIH Reporter API search query."""
    start_date, end_date = get_date_range()

    # Build keyword search string (OR logic)
    keyword_search = " OR ".join(f'"{kw}"' for kw in keywords)

    return {
        "criteria": {
            "activity_codes": ACTIVITY_CODES,
            "award_notice_date": {
                "from_date": start_date,
                "to_date": end_date
            },
            "newly_added_projects_only": True,
            "advanced_text_search": {
                "operator": "or",
                "search_field": "all",
                "search_text": keyword_search
            }
        },
        "include_fields": [
            "ApplId", "ProjectTitle", "AbstractText", "ProjectNum",
            "ContactPiName", "Organization", "AwardNoticeDate",
            "AwardAmount", "FiscalYear", "ProjectStartDate", "ProjectEndDate",
            "StudySection", "StudySectionName"
        ],
        "offset": 0,
        "limit": 500,
        "sort_field": "award_notice_date",
        "sort_order": "desc"
    }


def calculate_relevance_score(project: dict, keywords: list[str] = KEYWORDS) -> int:
    """Calculate relevance score based on keyword matches and study section.

    Scoring:
    - +9 for priority study sections (AVI, CDIN, CMAD, CMBG, CMND, BINP)
    - +3 for each keyword match in title
    - +1 for each keyword match in abstract
    """
    score = 0

    # Check study section - the API returns this as a dict with 'study_section_code'
    study_section = project.get("study_section") or {}
    if isinstance(study_section, dict):
        section_code = study_section.get("study_section_code", "")
    else:
        section_code = ""

    if section_code in PRIORITY_STUDY_SECTIONS:
        score += 9

    # Keyword matching
    title = (project.get("project_title") or "").lower()
    abstract = (project.get("abstract_text") or "").lower()

    for keyword in keywords:
        kw_lower = keyword.lower()
        # Title matches worth more
        if kw_lower in title:
            score += 3
        if kw_lower in abstract:
            score += 1

    return score


def fetch_new_awards(keywords: Optional[list[str]] = None) -> list[dict]:
    """Fetch new R01 awards matching keywords from NIH Reporter API."""
    if keywords is None:
        keywords = KEYWORDS

    query = build_search_query(keywords)

    try:
        response = requests.post(
            NIH_REPORTER_API_URL,
            json=query,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        response.raise_for_status()
        data = response.json()

        results = data.get("results", [])

        # Add relevance scores
        for project in results:
            project["relevance_score"] = calculate_relevance_score(project, keywords)

        # Filter by minimum relevance score
        results = [r for r in results if r.get("relevance_score", 0) >= MIN_RELEVANCE_SCORE]

        # Sort by relevance score (highest first)
        results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)

        return results

    except requests.RequestException as e:
        print(f"Error fetching NIH Reporter data: {e}")
        return []


def format_award_for_display(award: dict) -> dict:
    """Format a single award for display in the digest."""
    # Extract organization name from nested object
    org = award.get("organization", {})
    if isinstance(org, dict):
        org_name = org.get("org_name", "Unknown Organization")
        org_city = org.get("org_city", "")
        org_state = org.get("org_state", "")
        if org_city and org_state:
            org_display = f"{org_name} ({org_city}, {org_state})"
        else:
            org_display = org_name
    else:
        org_display = "Unknown Organization"

    # Extract study section
    study_section = award.get("study_section") or {}
    if isinstance(study_section, dict):
        section_code = study_section.get("study_section_code", "")
        section_name = study_section.get("study_section_name", "")
        study_section_display = f"{section_code}" if section_code else ""
    else:
        study_section_display = ""

    return {
        "title": award.get("project_title", "No title"),
        "pi_name": award.get("contact_pi_name", "Unknown PI"),
        "organization": org_display,
        "project_number": award.get("project_num", "N/A"),
        "award_date": award.get("award_notice_date", "N/A"),
        "award_amount": award.get("award_amount"),
        "abstract": award.get("abstract_text", "No abstract available"),
        "relevance_score": award.get("relevance_score", 0),
        "study_section": study_section_display,
        "nih_reporter_url": f"https://reporter.nih.gov/project-details/{award.get('appl_id', '')}"
    }
