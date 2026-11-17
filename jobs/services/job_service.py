"""
Job Management Service.
Handles job vacancy creation, updating, activation toggling, and pipeline statistics.
Fixes BUG-01: ensures the newly created Job instance is assigned to a variable and correctly logged.
"""

from typing import Dict, Any, Optional
from django.contrib.auth.models import User
from django.db import transaction
from django.utils.text import slugify

from jobs.models import Job
from applicants.services.activity_service import log_activity


@transaction.atomic
def create_job(data: Dict[str, Any], performed_by: Optional[User] = None) -> Job:
    """
    Creates a new job posting and logs the event in the activity trail.
    
    :param data: Dictionary containing title, slug, department, location, job_type, etc.
    :param performed_by: User performing the action.
    :return: Newly created Job instance.
    """
    title = data["title"]
    slug = data.get("slug")
    if not slug:
        slug = slugify(title)

    # Ensure unique slug if collision exists
    base_slug = slug
    counter = 1
    while Job.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    job = Job.objects.create(
        title=title,
        slug=slug,
        department=data.get("department", "General"),
        location=data.get("location", "Remote"),
        job_type=data.get("job_type", "Full Time"),
        description=data.get("description", ""),
        requirements=data.get("requirements", ""),
        responsibilities=data.get("responsibilities", ""),
        experience_required=int(data.get("experience_required", 0)),
        is_active=data.get("is_active", True),
    )

    # Associate required skills if passed
    required_skills = data.get("required_skills")
    if required_skills:
        job.required_skills.set(required_skills)

    log_activity(
        action=f"Job '{job.title}' created",
        performed_by=performed_by
    )

    return job


@transaction.atomic
def update_job(job: Job, data: Dict[str, Any], performed_by: Optional[User] = None) -> Job:
    """
    Updates an existing job vacancy and records the audit log.
    """
    job.title = data.get("title", job.title)
    if "slug" in data and data["slug"] != job.slug:
        # Check uniqueness
        new_slug = data["slug"]
        if not Job.objects.filter(slug=new_slug).exclude(pk=job.pk).exists():
            job.slug = new_slug

    job.department = data.get("department", job.department)
    job.location = data.get("location", job.location)
    job.job_type = data.get("job_type", job.job_type)
    job.description = data.get("description", job.description)
    job.requirements = data.get("requirements", job.requirements)
    job.responsibilities = data.get("responsibilities", job.responsibilities)
    if "experience_required" in data:
        job.experience_required = int(data["experience_required"])

    if "is_active" in data:
        job.is_active = bool(data["is_active"])

    job.save()

    if "required_skills" in data:
        job.required_skills.set(data["required_skills"])

    log_activity(
        action=f"Job '{job.title}' edited",
        performed_by=performed_by
    )

    return job


def toggle_job_status(job: Job, performed_by: Optional[User] = None) -> bool:
    """
    Toggles the active state of a job vacancy and writes to ActivityLog.
    
    :return: New active boolean status.
    """
    job.is_active = not job.is_active
    job.save(update_fields=["is_active"])

    status_str = "activated" if job.is_active else "deactivated"
    log_activity(
        action=f"Job '{job.title}' {status_str}",
        performed_by=performed_by
    )

    return job.is_active


def get_job_pipeline_stats(job: Job) -> Dict[str, int]:
    """
    Returns application count metrics broken down by recruitment stage for a specific job.
    """
    apps = job.applications.all()
    return {
        "total": apps.count(),
        "applied": apps.filter(status="Applied").count(),
        "under_review": apps.filter(status="Under Review").count(),
        "shortlisted": apps.filter(status="Shortlisted").count(),
        "interview_scheduled": apps.filter(status="Interview Scheduled").count(),
        "rejected": apps.filter(status="Rejected").count(),
        "hired": apps.filter(status="Hired").count(),
    }
