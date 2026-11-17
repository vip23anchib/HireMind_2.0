"""
Recruitment Analytics & Insights Service.
Calculates high-level recruitment metrics, skill distributions, and average experience trends,
and provides visualization compilation for templates and upcoming REST APIs.
"""

from typing import Dict, Any, List
from django.db.models import Count, Avg
import plotly.express as px
from plotly.offline import plot

from jobs.models import Job
from applicants.models import UserData, Application, Skill, UserSkill


def get_dashboard_metrics() -> Dict[str, Any]:
    """
    Computes high-level recruitment performance KPIs and pipeline conversion counts.
    """
    total_applications = Application.objects.count()
    active_jobs = Job.objects.filter(is_active=True).count()
    total_candidates = UserData.objects.count()
    total_skills = Skill.objects.count()
    total_user_skills = UserSkill.objects.count()

    shortlisted = Application.objects.filter(status='Shortlisted').count()
    interviews = Application.objects.filter(status='Interview Scheduled').count()
    hired = Application.objects.filter(status='Hired').count()
    under_review = Application.objects.filter(status='Under Review').count()
    rejected = Application.objects.filter(status='Rejected').count()
    applied = Application.objects.filter(status='Applied').count()

    recent_applications = list(
        Application.objects.select_related('candidate', 'job').order_by('-applied_at')[:5]
    )

    return {
        "total_applications": total_applications,
        "active_jobs": active_jobs,
        "total_candidates": total_candidates,
        "total_skills": total_skills,
        "total_user_skills": total_user_skills,
        "applied": applied,
        "under_review": under_review,
        "shortlisted": shortlisted,
        "interviews": interviews,
        "hired": hired,
        "rejected": rejected,
        "recent_applications": recent_applications,
    }


def get_skills_distribution(limit: int = 15) -> List[Dict[str, Any]]:
    """
    Retrieves the most prevalent candidate skills ordered by frequency.
    """
    top_skills_qs = (
        UserSkill.objects
        .values('skill__name')
        .annotate(total=Count('skill'))
        .order_by('-total')[:limit]
    )
    return [
        {"skill": item['skill__name'], "total": item['total']}
        for item in top_skills_qs
    ]


def get_experience_distribution(limit: int = 15) -> List[Dict[str, Any]]:
    """
    Retrieves the average years of experience per technology.
    """
    avg_exp_qs = (
        UserSkill.objects
        .values('skill__name')
        .annotate(avg_years=Avg('years_of_experience'))
        .order_by('-avg_years')[:limit]
    )
    return [
        {
            "skill": item['skill__name'],
            "avg_years": round(item['avg_years'], 2) if item['avg_years'] else 0.0
        }
        for item in avg_exp_qs
    ]


def build_plotly_charts(
    skills_data: List[Dict[str, Any]],
    experience_data: List[Dict[str, Any]]
) -> Dict[str, str]:
    """
    Generates offline HTML div strings for Plotly charts to support existing template views.
    """
    skills = [item["skill"] for item in skills_data]
    counts = [item["total"] for item in skills_data]

    if skills:
        fig_skills = px.bar(x=skills, y=counts, title="Top Skills Distribution")
        skills_chart_div = plot(fig_skills, output_type='div', include_plotlyjs=False)
    else:
        skills_chart_div = "<p>No skills data available.</p>"

    exp_skills = [item["skill"] for item in experience_data]
    exp_years = [item["avg_years"] for item in experience_data]

    if exp_skills:
        fig_exp = px.bar(x=exp_skills, y=exp_years, title="Average Experience By Skill (Years)")
        exp_chart_div = plot(fig_exp, output_type='div', include_plotlyjs=False)
    else:
        exp_chart_div = "<p>No experience data available.</p>"

    return {
        "skills_chart": skills_chart_div,
        "experience_chart": exp_chart_div,
    }
