"""
Form Helper compatibility module.
Delegates to applicants.services modules while preserving legacy imports and fixing BUG-04.
"""

from ..services.resume_parser import (
    extract_pdf_text,
    is_valid_resume as is_resume,
    extract_email,
    extract_phone,
    extract_experience_text as extract_experience,
    extract_skill_experience,
    extract_metadata_from_text,
)
from ..services.skill_service import (
    SKILL_DATABASE,
    SKILL_SYNONYMS,
    normalize_skill_name as normalize_skill,
    extract_skills_from_text as extract_skills_from_database,
)

# Fix BUG-04: alias SKILLS to SKILL_DATABASE so legacy references do not crash
SKILLS = SKILL_DATABASE


def extract_skills(text: str):
    """
    Backwards-compatible wrapper.
    Fixes BUG-04 by safely utilizing canonical skill catalog.
    """
    return extract_skills_from_database(text)
