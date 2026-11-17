"""
Resumes API Views.
Handles resume uploads, validation, document record creation, and status polling.
"""

from rest_framework import views, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse

from applicants.models import Document, UserData
from jobs.models import Job
from applicants.services.resume_parser import extract_pdf_text, extract_metadata_from_text
from applicants.services.skill_service import extract_skills_from_text, sync_candidate_skills
from applicants.services.matching_service import calculate_ats_match
from applicants.services.activity_service import log_activity
from .serializers import ResumeUploadSerializer, ResumeStatusSerializer


class ResumeUploadAPIView(views.APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        request=ResumeUploadSerializer,
        responses={
            201: ResumeStatusSerializer,
            400: OpenApiResponse(description="Validation error")
        },
        description="Upload a candidate PDF resume and trigger parsing/skill extraction."
    )
    def post(self, request):
        serializer = ResumeUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file = serializer.validated_data['file']
        candidate_id = serializer.validated_data.get('candidate_id')
        job_id = serializer.validated_data.get('job_id')

        candidate = None
        if candidate_id:
            candidate = get_object_or_404(UserData, id=candidate_id)

        # Ingest and parse
        extracted_text = extract_pdf_text(file)
        metadata = extract_metadata_from_text(extracted_text)
        detected_skills = extract_skills_from_text(extracted_text)

        if candidate:
            sync_candidate_skills(
                candidate=candidate,
                detected_skills=detected_skills,
                skill_experience_map=metadata["skill_experience"]
            )

        document = Document.objects.create(
            user=request.user if request.user.is_authenticated else None,
            user_data=candidate,
            file=file,
            pdf_text=extracted_text,
            additional_info=metadata["additional_info"],
            experience_info=metadata["experience_info"],
            status='Completed'
        )

        log_activity(
            action=f"Resume uploaded and processed (Document #{document.id})",
            candidate=candidate,
            performed_by=request.user
        )

        return Response(
            ResumeStatusSerializer(document).data,
            status=status.HTTP_201_CREATED
        )


class ResumeStatusAPIView(views.APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        responses={200: ResumeStatusSerializer},
        description="Poll resume ingestion and parsing status."
    )
    def get(self, request, id):
        document = get_object_or_404(Document, id=id)
        return Response(ResumeStatusSerializer(document).data, status=status.HTTP_200_OK)
