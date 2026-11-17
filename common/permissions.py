"""
Custom DRF Permissions for HireMind ATS.
Protects recruiter-only and admin-only endpoints.
"""

from rest_framework import permissions


class IsRecruiterOrAdmin(permissions.BasePermission):
    """
    Allows access only to authenticated users who are staff, superusers, or have a Member profile.
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.user.is_staff or request.user.is_superuser:
            return True
        return hasattr(request.user, 'member')


class IsAdminUserRole(permissions.BasePermission):
    """
    Allows access only to users who are superusers or members with role == 'Admin'.
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.user.is_superuser:
            return True
        if hasattr(request.user, 'member'):
            return request.user.member.role == 'Admin'
        return False
