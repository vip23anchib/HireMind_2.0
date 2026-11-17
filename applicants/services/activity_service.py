"""
Activity Logging Service.
Provides a standardized interface for recording recruiter and candidate lifecycle events.
Fixes BUG-03: previously referenced obsolete 'user' field instead of 'performed_by'.
"""

from typing import Optional
from django.contrib.auth.models import User
from applicants.models import ActivityLog, UserData


def log_activity(
    action: str,
    candidate: Optional[UserData] = None,
    performed_by: Optional[User] = None
) -> ActivityLog:
    """
    Records an activity log event in the database.
    
    :param action: Human-readable action description.
    :param candidate: Optional UserData instance the action pertains to.
    :param performed_by: Optional User instance who performed the action (recruiter or admin).
    :return: Created ActivityLog instance.
    """
    user = performed_by if (performed_by and getattr(performed_by, 'is_authenticated', False)) else None
    return ActivityLog.objects.create(
        action=action,
        candidate=candidate,
        performed_by=user,
    )
