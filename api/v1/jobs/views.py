"""
Jobs API ViewSet.
Provides CRUD, filtering, searching, activation toggling, and stage statistics for job postings.
"""

from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiResponse

from jobs.models import Job
from common.permissions import IsRecruiterOrAdmin
from jobs.services.job_service import toggle_job_status, get_job_pipeline_stats
from .serializers import JobSerializer, JobListSerializer, JobStatisticsSerializer


class JobViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department', 'job_type', 'is_active', 'experience_required']
    search_fields = ['title', 'description', 'requirements', 'location', 'department']
    ordering_fields = ['created_at', 'title', 'experience_required']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        queryset = Job.objects.prefetch_related('required_skills', 'applications').all()

        # Public applicants only see active vacancies
        if not (user and user.is_authenticated):
            return queryset.filter(is_active=True)

        # Allow recruiter to filter specifically if requested
        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return JobListSerializer
        return JobSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [IsRecruiterOrAdmin()]

    @extend_schema(
        responses={200: OpenApiResponse(description="Job status successfully toggled.")},
        description="Toggle job vacancy between active and inactive states."
    )
    @action(detail=True, methods=['post'], url_path='toggle-status')
    def toggle_status(self, request, id=None):
        job = self.get_object()
        new_status = toggle_job_status(job=job, performed_by=request.user)
        return Response({
            "id": job.id,
            "title": job.title,
            "is_active": new_status,
            "message": f"Job '{job.title}' is now {'active' if new_status else 'inactive'}."
        }, status=status.HTTP_200_OK)

    @extend_schema(
        responses={200: JobStatisticsSerializer},
        description="Retrieve application pipeline statistics for this job opening."
    )
    @action(detail=True, methods=['get'], url_path='statistics')
    def statistics(self, request, id=None):
        job = self.get_object()
        stats = get_job_pipeline_stats(job)
        return Response(stats, status=status.HTTP_200_OK)

    @extend_schema(
        description="List all applications submitted for this specific job."
    )
    @action(detail=True, methods=['get'], url_path='applications')
    def applications(self, request, id=None):
        job = self.get_object()
        from api.v1.applications.serializers import ApplicationListSerializer
        applications = job.applications.select_related('candidate').all()
        page = self.paginate_queryset(applications)
        if page is not None:
            serializer = ApplicationListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ApplicationListSerializer(applications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
