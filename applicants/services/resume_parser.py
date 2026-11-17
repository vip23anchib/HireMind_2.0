"""
Resume Parsing & Text Extraction Service.
Extracts raw text, contact information, and experience timelines from candidate resumes.
"""

import re
import logging
from typing import Dict, Optional, Tuple, Any
from pypdf import PdfReader

logger = logging.getLogger(__name__)

RESUME_ANCHOR_KEYWORDS = [
    "skills",
    "experience",
    "education",
    "projects",
    "certifications",
    "linkedin",
    "resume",
    "internship",
    "summary",
    "employment",
]

EMAIL_PATTERN = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')
PHONE_PATTERN = re.compile(r'\+?\d[\d\s-]{8,15}')
EXPERIENCE_PATTERN = re.compile(r'(\d+)\s*(?:years?|yrs?)', re.IGNORECASE)

SKILL_EXP_PATTERNS = [
    re.compile(r'([A-Za-z0-9.+# ]+?)\s*-\s*(\d+)\s+years', re.IGNORECASE),
    re.compile(r'([A-Za-z0-9.+# ]+?)\s*\(\s*(\d+)\s+years?\s*\)', re.IGNORECASE),
]


def extract_pdf_text(pdf_file) -> str:
    """
    Extracts concatenated textual content from all pages of an uploaded PDF file.
    
    :param pdf_file: File-like object or path to a PDF.
    :return: Extracted text string or empty string on failure.
    """
    if not pdf_file:
        return ""
    try:
        if hasattr(pdf_file, 'seek'):
            pdf_file.seek(0)
        reader = PdfReader(pdf_file)
        pages_text = []
        for index, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                pages_text.append(page_text)
        return "\n".join(pages_text).strip()
    except Exception as exc:
        logger.warning("Failed to extract PDF text: %s", exc)
        return ""


def is_valid_resume(text: str, threshold: int = 3) -> bool:
    """
    Heuristically evaluates whether extracted text resembles a CV/resume based on keyword density.
    
    :param text: Document text to inspect.
    :param threshold: Minimum number of keywords required.
    :return: True if text meets criteria, False otherwise.
    """
    if not text:
        return False
    lower_text = text.lower()
    score = sum(1 for kw in RESUME_ANCHOR_KEYWORDS if kw in lower_text)
    return score >= threshold


def extract_email(text: str) -> str:
    """Extracts first valid email address found in the text."""
    if not text:
        return ""
    match = EMAIL_PATTERN.search(text)
    return match.group(0) if match else ""


def extract_phone(text: str) -> str:
    """Extracts first phone number string found in the text."""
    if not text:
        return ""
    match = PHONE_PATTERN.search(text)
    return match.group(0).strip() if match else ""


def extract_experience_text(text: str) -> str:
    """Extracts stated total experience span (e.g., '5 years') from text."""
    if not text:
        return ""
    match = EXPERIENCE_PATTERN.search(text)
    return match.group(0) if match else ""


def extract_skill_experience(text: str) -> Dict[str, int]:
    """
    Extracts technology-specific experience mappings such as 'Python - 3 years' or 'React (2 years)'.
    
    :param text: Raw text from resume.
    :return: Dictionary mapping skill names to integer years of experience.
    """
    if not text:
        return {}
    experience_data: Dict[str, int] = {}
    for pattern in SKILL_EXP_PATTERNS:
        for skill_match, years_match in pattern.findall(text):
            cleaned_skill = skill_match.strip()
            if cleaned_skill and len(cleaned_skill) < 40:
                try:
                    experience_data[cleaned_skill] = int(years_match)
                except ValueError:
                    continue
    return experience_data


def extract_metadata_from_text(text: str) -> Dict[str, Any]:
    """
    Consolidates contact information, general experience, and skill-specific experience
    into structured metadata and human-readable string summaries for Document models.
    """
    email = extract_email(text)
    phone = extract_phone(text)
    overall_exp = extract_experience_text(text)
    skill_exp = extract_skill_experience(text)

    additional_info_parts = []
    if email:
        additional_info_parts.append(f"Email: {email}")
    if phone:
        additional_info_parts.append(f"Phone: {phone}")
    if overall_exp:
        additional_info_parts.append(f"Experience: {overall_exp}")
    additional_info = "\n".join(additional_info_parts)

    formatted_exp_parts = [
        f"{skill}: {years} years" for skill, years in skill_exp.items()
    ]
    experience_info = "\n".join(formatted_exp_parts)

    return {
        "email": email,
        "phone": phone,
        "overall_experience": overall_exp,
        "skill_experience": skill_exp,
        "additional_info": additional_info,
        "experience_info": experience_info,
    }
