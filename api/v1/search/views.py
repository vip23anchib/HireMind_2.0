"""
Search and Matching API Views.
Exposes multi-skill candidate search engine and candidate-job ATS match gap analysis.
"""

from rest_framework import views, status, permissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from common.permissions import IsRecruiterOrAdmin
from applicants.models import UserData
from jobs.models import Job
from applicants.services.search_service import search_candidates_service
from applicants.services.matching_service import calculate_ats_match

from .serializers import (
    CandidateSearchResponseSerializer,
    CandidateJobMatchResponseSerializer,
)


class CandidateSearchAPIView(views.APIView):
    permission_classes = [IsRecruiterOrAdmin]

    @extend_schema(
        parameters=[
            OpenApiParameter(name='skill', description='Comma-separated skills (e.g. "Python, Django")', required=False, type=str),
            OpenApiParameter(name='experience', description='Minimum experience in years', required=False, type=int),
            OpenApiParameter(name='search_type', description='Search operator: "or" (default) or "and"', required=False, type=str),
        ],
        responses={200: CandidateSearchResponseSerializer},
        description="Search candidates by skills with boolean AND/OR operator and experience threshold."
    )
    def get(self, request):
        skill_query = request.GET.get('skill', '').strip()
        experience_param = request.GET.get('experience', '').strip()
        search_type = request.GET.get('search_type', 'or').strip()

        min_experience = int(experience_param) if (experience_param and experience_param.isdigit()) else None

        search_result = search_candidates_service(
            skill_query=skill_query,
            min_experience=min_experience,
            search_type=search_type
        )

        serializer = CandidateSearchResponseSerializer(search_result)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CandidateJobMatchAPIView(views.APIView):
    permission_classes = [IsRecruiterOrAdmin]

    @extend_schema(
        parameters=[
            OpenApiParameter(name='candidate_id', description='Candidate ID', required=True, type=int),
            OpenApiParameter(name='job_id', description='Job vacancy ID', required=True, type=int),
        ],
        responses={200: CandidateJobMatchResponseSerializer},
        description="Compute deterministic ATS match score and skill gaps between a candidate and a job opening."
    )
    def get(self, request):
        candidate_id = request.GET.get('candidate_id')
        job_id = request.GET.get('job_id')

        if not candidate_id or not job_id:
            return Response(
                {"message": "Both candidate_id and job_id query parameters are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        candidate = get_object_or_404(UserData, id=candidate_id)
        job = get_object_or_404(Job, id=job_id)

        match_data = calculate_ats_match(candidate, job)
        serializer = CandidateJobMatchResponseSerializer(match_data)
        return Response(serializer.data, status=status.HTTP_200_OK)
