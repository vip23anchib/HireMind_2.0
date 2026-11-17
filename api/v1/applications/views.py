"""
Applications API ViewSet.
Handles recruitment pipeline, stage transitions, status audit history, and application submissions.
"""

from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from drf_spectacular.utils import extend_schema, OpenApiResponse

from applicants.models import Application, ApplicationStatusHistory, UserData, Document
from jobs.models import Job
from common.permissions import IsRecruiterOrAdmin
from applicants.services.activity_service import log_activity
from applicants.services.resume_parser import extract_pdf_text, extract_metadata_from_text
from applicants.services.skill_service import extract_skills_from_text, sync_candidate_skills
from applicants.services.matching_service import calculate_ats_match

from .serializers import (
    ApplicationListSerializer,
    ApplicationDetailSerializer,
    ApplicationStatusUpdateSerializer,
    ApplicationStatusHistorySerializer,
    ApplicationCreateSerializer,
)


class ApplicationViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['job', 'status']
    search_fields = ['candidate__name', 'candidate__email', 'job__title']
    ordering_fields = ['applied_at', 'ats_score']
    ordering = ['-applied_at']

    def get_queryset(self):
        return Application.objects.select_related('candidate', 'job').prefetch_related('status_history').all()

    def get_serializer_class(self):
        if self.action == 'list':
            return ApplicationListSerializer
        if self.action == 'create':
            return ApplicationCreateSerializer
        return ApplicationDetailSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [IsRecruiterOrAdmin()]

    def create(self, request, *args, **kwargs):
        """
        Public or recruiter candidate application submission with PDF resume.
        """
        serializer = ApplicationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        with transaction.atomic():
            job = Job.objects.get(id=data['job_id'])

            # 1. Candidate lookup or creation
            candidate, _ = UserData.objects.get_or_create(
                email=data['email'],
                defaults={
                    "name": data['name'],
                    "gender": data.get('gender', 'Not Specified'),
                    "phone_number": data.get('phone_number'),
                    "country": data.get('country', 'Global'),
                    "cover_letter": data.get('cover_letter'),
                    "linkedin_url": data.get('linkedin_url'),
                    "portfolio_url": data.get('portfolio_url'),
                    "user": request.user if request.user.is_authenticated else None,
                }
            )

            # 2. Ingest Resume
            uploaded_file = data['resume_file']
            extracted_text = extract_pdf_text(uploaded_file)
            metadata = extract_metadata_from_text(extracted_text)
            detected_skills = extract_skills_from_text(extracted_text)

            # Sync skills
            sync_candidate_skills(
                candidate=candidate,
                detected_skills=detected_skills,
                skill_experience_map=metadata["skill_experience"]
            )

            # Save Document
            document = Document.objects.create(
                user_data=candidate,
                user=request.user if request.user.is_authenticated else None,
                file=uploaded_file,
                pdf_text=extracted_text,
                additional_info=metadata["additional_info"],
                experience_info=metadata["experience_info"],
                status='Completed'
            )

            # 3. Calculate ATS Match Score
            match_result = calculate_ats_match(candidate, job)
            score = match_result['score']

            # 4. Create Application
            application = Application.objects.create(
                candidate=candidate,
                job=job,
                status='Applied',
                ats_score=score
            )

            # 5. Record Initial Status History
            ApplicationStatusHistory.objects.create(
                application=application,
                old_status="None",
                new_status="Applied",
                changed_by=request.user if request.user.is_authenticated else None,
                notes="Initial application submission"
            )

            log_activity(
                action=f"Applied for '{job.title}' with ATS match {score}%",
                candidate=candidate,
                performed_by=request.user
            )

        return Response(
            ApplicationDetailSerializer(application, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    @extend_schema(
        request=ApplicationStatusUpdateSerializer,
        responses={200: ApplicationDetailSerializer},
        description="Transition application to a new recruitment stage and log history."
    )
    @action(detail=True, methods=['patch'], url_path='status')
    def update_status(self, request, id=None):
        application = self.get_object()
        serializer = ApplicationStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_status = serializer.validated_data['status']
        notes = serializer.validated_data.get('notes', '')

        if new_status != application.status:
            old_status = application.status
            application.status = new_status
            application.save(update_fields=['status'])

            ApplicationStatusHistory.objects.create(
                application=application,
                old_status=old_status,
                new_status=new_status,
                changed_by=request.user,
                notes=notes
            )

            log_activity(
                action=f"Application status changed to '{new_status}' for {application.candidate.name}",
                candidate=application.candidate,
                performed_by=request.user
            )

        return Response(
            ApplicationDetailSerializer(application, context={'request': request}).data,
            status=status.HTTP_200_OK
        )

    @extend_schema(
        responses={200: ApplicationStatusHistorySerializer(many=True)},
        description="List full status audit trail for this application."
    )
    @action(detail=True, methods=['get'], url_path='history')
    def history(self, request, id=None):
        application = self.get_object()
        history_records = application.status_history.all()
        serializer = ApplicationStatusHistorySerializer(history_records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
