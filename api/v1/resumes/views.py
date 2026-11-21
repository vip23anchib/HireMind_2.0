"""
Resumes API Views.
Handles resume uploads, validation, document record creation, and status polling.
"""

from rest_framework import views, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse

from applicants.models import Document, UserData
from applicants.tasks import process_resume_task
from applicants.services.activity_service import log_activity
from .serializers import ResumeUploadSerializer, ResumeStatusSerializer


class ResumeUploadAPIView(views.APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        request=ResumeUploadSerializer,
        responses={
            201: ResumeStatusSerializer,
            202: ResumeStatusSerializer,
            400: OpenApiResponse(description="Validation error")
        },
        description="Upload a candidate PDF resume and queue asynchronous parsing and skill extraction."
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

        document = Document.objects.create(
            user=request.user if request.user.is_authenticated else None,
            user_data=candidate,
            file=file,
            status='Queued'
        )

        log_activity(
            action=f"Resume uploaded and queued for processing (Document #{document.id})",
            candidate=candidate,
            performed_by=request.user if request.user.is_authenticated else None
        )

        # Trigger async parsing task
        task = process_resume_task.delay(document.id)

        # If eager execution ran, refresh document from DB to get the latest status
        document.refresh_from_db()

        response_status = status.HTTP_201_CREATED if document.status == 'Completed' else status.HTTP_202_ACCEPTED
        data = ResumeStatusSerializer(document).data
        data['task_id'] = task.id if task else None
        return Response(data, status=response_status)


class ResumeStatusAPIView(views.APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        responses={200: ResumeStatusSerializer},
        description="Poll resume ingestion and parsing status."
    )
    def get(self, request, id):
        document = get_object_or_404(Document, id=id)
        return Response(ResumeStatusSerializer(document).data, status=status.HTTP_200_OK)
