"""
ATS Candidate-Job Matching Service.
Implements deterministic, explainable match scoring between candidate profiles and job requirements.
"""

from typing import Dict, Any, Set
from applicants.models import UserData, UserSkill
from jobs.models import Job


def calculate_ats_match(candidate: UserData, job: Job) -> Dict[str, Any]:
    """
    Computes deterministic ATS match score and skill gap breakdown for a candidate against a job vacancy.
    
    :param candidate: UserData candidate instance.
    :param job: Job instance with required_skills.
    :return: Dictionary containing:
        - score: Float percentage (0.0 to 100.0)
        - matched_skills: List of matching skill names
        - missing_skills: List of job required skills the candidate lacks
        - candidate_skills: Full list of candidate skills
        - required_skills: Full list of job required skills
    """
    candidate_skills: Set[str] = set(
        UserSkill.objects.filter(user_data=candidate).values_list('skill__name', flat=True)
    )

    required_skills: Set[str] = set(
        job.required_skills.values_list('name', flat=True)
    )

    matched: Set[str] = candidate_skills & required_skills
    missing: Set[str] = required_skills - candidate_skills

    if len(required_skills) > 0:
        score = round((len(matched) / len(required_skills)) * 100, 2)
    else:
        # If no specific skills required for the job, default score is 100.0 or 0.0 based on candidate having profile
        score = 100.0 if candidate_skills else 0.0

    return {
        "score": score,
        "matched_skills": sorted(list(matched)),
        "missing_skills": sorted(list(missing)),
        "candidate_skills": sorted(list(candidate_skills)),
        "required_skills": sorted(list(required_skills)),
        "total_required": len(required_skills),
        "total_matched": len(matched),
    }
