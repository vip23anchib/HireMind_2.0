"""
ATS Candidate Search Engine Service.
Executes multi-skill queries with boolean AND/OR semantics, experience threshold filtering,
ATS match scoring, and missing skills gap calculation.
Fixes BUG-02: resolves undefined 'requested_count' variable.
"""

import time
from typing import List, Dict, Any, Optional, Set
from django.db.models import Q
from applicants.models import UserSkill, UserData


def search_candidates_service(
    skill_query: str,
    min_experience: Optional[int] = None,
    search_type: str = "or"
) -> Dict[str, Any]:
    """
    Searches candidates by technical skills and experience.
    
    :param skill_query: Comma-separated list of skills (e.g. 'Python, Django, React').
    :param min_experience: Minimum years of experience threshold.
    :param search_type: 'or' (union) or 'and' (intersection).
    :return: Dictionary containing candidate_results, total_matches, execution_time_seconds, and parsed_skills.
    """
    start_time = time.perf_counter()

    skills_list = [
        s.strip() for s in skill_query.split(',') if s.strip()
    ]
    requested_count = len(skills_list)

    if requested_count == 0:
        return {
            "candidate_results": [],
            "total_matches": 0,
            "execution_time_seconds": round(time.perf_counter() - start_time, 6),
            "skills_list": [],
            "search_type": search_type,
            "min_experience": min_experience,
        }

    # 1. Execute Query Branch
    if search_type.lower() == "or":
        or_filter = Q()
        for skill_name in skills_list:
            or_filter |= Q(skill__name__iexact=skill_name)
        matched_user_skills = UserSkill.objects.filter(or_filter)
    else:
        # Boolean AND Branch: Set Intersection across candidate IDs
        candidate_ids: Optional[Set[int]] = None
        for skill_name in skills_list:
            matching_ids = set(
                UserSkill.objects.filter(skill__name__iexact=skill_name).values_list('user_data_id', flat=True)
            )
            if candidate_ids is None:
                candidate_ids = matching_ids
            else:
                candidate_ids = candidate_ids & matching_ids

        if not candidate_ids:
            return {
                "candidate_results": [],
                "total_matches": 0,
                "execution_time_seconds": round(time.perf_counter() - start_time, 6),
                "skills_list": skills_list,
                "search_type": search_type,
                "min_experience": min_experience,
            }

        matched_user_skills = UserSkill.objects.filter(user_data_id__in=candidate_ids)

        # Filter rows to only the searched skills for clean presentation
        prune_filter = Q()
        for skill_name in skills_list:
            prune_filter |= Q(skill__name__iexact=skill_name)
        matched_user_skills = matched_user_skills.filter(prune_filter)

    # 2. Filter by minimum experience if provided
    if min_experience is not None and min_experience > 0:
        matched_user_skills = matched_user_skills.filter(years_of_experience__gte=min_experience)

    matched_user_skills = matched_user_skills.select_related('user_data', 'skill').order_by('-years_of_experience')

    # 3. Aggregate results per candidate
    candidate_map: Dict[int, Dict[str, Any]] = {}
    for item in matched_user_skills:
        cid = item.user_data.id
        exp = item.years_of_experience or 0
        if cid not in candidate_map:
            candidate_map[cid] = {
                "candidate": item.user_data,
                "skills": [item.skill.name],
                "experience": exp,
            }
        else:
            if item.skill.name not in candidate_map[cid]["skills"]:
                candidate_map[cid]["skills"].append(item.skill.name)
            candidate_map[cid]["experience"] = max(candidate_map[cid]["experience"], exp)

    # 4. Calculate ATS match score and missing skills for each candidate
    # (Fixes BUG-02: requested_count is cleanly in scope)
    candidate_results: List[Dict[str, Any]] = []
    requested_skills_lower = {s.lower().strip() for s in skills_list}

    for data in candidate_map.values():
        candidate_skills_lower = {s.lower().strip() for s in data["skills"]}
        matched_count = len(candidate_skills_lower & requested_skills_lower)

        score = round((matched_count / requested_count) * 100)
        data["score"] = score

        missing_skills = requested_skills_lower - candidate_skills_lower
        data["missing_skills"] = [
            s for s in skills_list if s.lower().strip() in missing_skills
        ]

        candidate_results.append(data)

    # 5. Sort descending by ATS Score, then by Experience
    candidate_results.sort(
        key=lambda x: (x["score"], x["experience"]),
        reverse=True
    )

    execution_time = round(time.perf_counter() - start_time, 6)

    return {
        "candidate_results": candidate_results,
        "total_matches": len(candidate_results),
        "execution_time_seconds": execution_time,
        "skills_list": skills_list,
        "search_type": search_type,
        "min_experience": min_experience,
        "raw_queryset": matched_user_skills,
    }
