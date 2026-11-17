"""
Utility helpers for the applicants app.
Delegates to applicants.services.activity_service to ensure attribute compatibility.
"""

from .services.activity_service import log_activity


def create_log(user, action, candidate=None):
    """
    Backwards-compatible wrapper around log_activity.
    Fixes BUG-03 (previously used obsolete field name 'user').
    """
    return log_activity(action=action, candidate=candidate, performed_by=user)
