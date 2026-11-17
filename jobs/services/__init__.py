"""
Jobs Domain Services.
Encapsulates business logic for job vacancies, status toggling, and recruitment pipeline statistics.
"""

from .job_service import (
    create_job,
    update_job,
    toggle_job_status,
    get_job_pipeline_stats,
)

__all__ = [
    "create_job",
    "update_job",
    "toggle_job_status",
    "get_job_pipeline_stats",
]
