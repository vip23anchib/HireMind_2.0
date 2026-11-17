"""
Applicants Domain Services.
Centralizes business logic for resume parsing, skill management, matching, candidate search, and analytics.
"""

from .activity_service import log_activity
from .resume_parser import extract_pdf_text, is_valid_resume, extract_metadata_from_text
from .skill_service import (
    SKILL_DATABASE,
    SKILL_SYNONYMS,
    normalize_skill_name,
    extract_skills_from_text,
    sync_candidate_skills,
)
from .matching_service import calculate_ats_match
from .search_service import search_candidates_service
from .analytics_service import get_dashboard_metrics, get_skills_distribution, get_experience_distribution

__all__ = [
    "log_activity",
    "extract_pdf_text",
    "is_valid_resume",
    "extract_metadata_from_text",
    "SKILL_DATABASE",
    "SKILL_SYNONYMS",
    "normalize_skill_name",
    "extract_skills_from_text",
    "sync_candidate_skills",
    "calculate_ats_match",
    "search_candidates_service",
    "get_dashboard_metrics",
    "get_skills_distribution",
    "get_experience_distribution",
]
