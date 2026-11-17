"""
Candidates API ViewSet.
Provides candidate search, profiles, CRUD operations, application history, and secure resume streaming.
"""

from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import FileResponse, Http404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiResponse

from applicants.models import UserData, Document, Application
from common.permissions import IsRecruiterOrAdmin
from applicants.services.activity_service import log_activity

from .serializers import (
    CandidateListSerializer,
    CandidateDetailSerializer,
    CandidateCreateUpdateSerializer,
)


class CandidateViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    permission_classes = [IsRecruiterOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['country', 'gender']
    search_fields = ['name', 'email', 'phone_number', 'user_skills__skill__name']
    ordering_fields = ['id', 'name']
    ordering = ['id']

    def get_queryset(self):
        return (
            UserData.objects
            .prefetch_related('user_skills__skill', 'applications__job', 'documents')
            .all()
        )

    def get_serializer_class(self):
        if self.action == 'list':
            return CandidateListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return CandidateCreateUpdateSerializer
        return CandidateDetailSerializer

    def perform_create(self, serializer):
        candidate = serializer.save()
        log_activity(
            action=f"Created candidate profile for '{candidate.name}'",
            candidate=candidate,
            performed_by=self.request.user
        )

    def perform_update(self, serializer):
        candidate = serializer.save()
        log_activity(
            action=f"Updated candidate profile for '{candidate.name}'",
            candidate=candidate,
            performed_by=self.request.user
        )

    def perform_destroy(self, instance):
        name = instance.name
        log_activity(
            action=f"Deleted candidate profile '{name}'",
            performed_by=self.request.user
        )
        instance.delete()

    @extend_schema(
        responses={
            200: OpenApiResponse(description="Binary PDF file response."),
            404: OpenApiResponse(description="No resume found for candidate.")
        },
        description="Securely stream candidate resume PDF with recruiter authorization."
    )
    @action(detail=True, methods=['get'], url_path='resume')
    def resume(self, request, id=None):
        candidate = self.get_object()
        doc = candidate.documents.filter(status='Completed').first() or candidate.documents.first()

        if not doc or not doc.file:
            raise Http404("Resume document does not exist for this candidate.")

        log_activity(
            action=f"Downloaded/viewed resume for candidate '{candidate.name}'",
            candidate=candidate,
            performed_by=request.user
        )

        return FileResponse(
            doc.file.open('rb'),
            content_type='application/pdf',
            as_attachment=False,
            filename=f"Resume_{candidate.name.replace(' ', '_')}.pdf"
        )

    @extend_schema(
        description="List all job applications submitted by this candidate."
    )
    @action(detail=True, methods=['get'], url_path='applications')
    def applications(self, request, id=None):
        candidate = self.get_object()
        from api.v1.applications.serializers import ApplicationListSerializer
        apps = candidate.applications.select_related('job').all()
        serializer = ApplicationListSerializer(apps, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
