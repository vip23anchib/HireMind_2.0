"""
Activity Logs API Views.
Provides paginated audit trail of all recruiter actions and system events.
"""

from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema

from applicants.models import ActivityLog
from common.permissions import IsRecruiterOrAdmin
from .serializers import ActivityLogSerializer


class ActivityLogListAPIView(generics.ListAPIView):
    permission_classes = [IsRecruiterOrAdmin]
    serializer_class = ActivityLogSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['candidate', 'performed_by']
    search_fields = ['action', 'candidate__name', 'performed_by__username']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return ActivityLog.objects.select_related('candidate', 'performed_by').all()

    @extend_schema(
        description="Retrieve paginated list of recruitment audit trail logs."
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
