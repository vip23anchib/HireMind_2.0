"""
Analytics API Views.
Provides real-time recruitment metrics, skill distributions, and pipeline conversion trends.
"""

from rest_framework import views, status, permissions
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter

from common.permissions import IsRecruiterOrAdmin
from applicants.services.analytics_service import (
    get_dashboard_metrics,
    get_skills_distribution,
    get_experience_distribution,
)

from .serializers import (
    AnalyticsDashboardSerializer,
    SkillDistributionItemSerializer,
    ExperienceDistributionItemSerializer,
    FunnelStageSerializer,
)


class AnalyticsDashboardAPIView(views.APIView):
    permission_classes = [IsRecruiterOrAdmin]

    @extend_schema(
        responses={200: AnalyticsDashboardSerializer},
        description="Retrieve core recruitment KPIs, total counts, and stage totals."
    )
    def get(self, request):
        metrics = get_dashboard_metrics()
        serializer = AnalyticsDashboardSerializer(metrics)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SkillsDistributionAPIView(views.APIView):
    permission_classes = [IsRecruiterOrAdmin]

    @extend_schema(
        parameters=[
            OpenApiParameter(name='limit', description='Number of top skills to return (default: 15)', required=False, type=int),
        ],
        responses={200: SkillDistributionItemSerializer(many=True)},
        description="Retrieve frequency distribution of top candidate technical skills."
    )
    def get(self, request):
        limit = int(request.GET.get('limit', 15))
        skills_data = get_skills_distribution(limit=limit)
        serializer = SkillDistributionItemSerializer(skills_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ExperienceDistributionAPIView(views.APIView):
    permission_classes = [IsRecruiterOrAdmin]

    @extend_schema(
        parameters=[
            OpenApiParameter(name='limit', description='Number of skills to return (default: 15)', required=False, type=int),
        ],
        responses={200: ExperienceDistributionItemSerializer(many=True)},
        description="Retrieve average years of candidate experience grouped by technology."
    )
    def get(self, request):
        limit = int(request.GET.get('limit', 15))
        exp_data = get_experience_distribution(limit=limit)
        serializer = ExperienceDistributionItemSerializer(exp_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RecruitmentFunnelAPIView(views.APIView):
    permission_classes = [IsRecruiterOrAdmin]

    @extend_schema(
        responses={200: FunnelStageSerializer(many=True)},
        description="Retrieve candidate volume and conversion percentages through each pipeline stage."
    )
    def get(self, request):
        metrics = get_dashboard_metrics()
        total = metrics['total_applications'] or 1

        stages = [
            {"stage": "Applied", "count": metrics['applied'], "percentage_of_total": round((metrics['applied'] / total) * 100, 1)},
            {"stage": "Under Review", "count": metrics['under_review'], "percentage_of_total": round((metrics['under_review'] / total) * 100, 1)},
            {"stage": "Shortlisted", "count": metrics['shortlisted'], "percentage_of_total": round((metrics['shortlisted'] / total) * 100, 1)},
            {"stage": "Interview Scheduled", "count": metrics['interviews'], "percentage_of_total": round((metrics['interviews'] / total) * 100, 1)},
            {"stage": "Hired", "count": metrics['hired'], "percentage_of_total": round((metrics['hired'] / total) * 100, 1)},
            {"stage": "Rejected", "count": metrics['rejected'], "percentage_of_total": round((metrics['rejected'] / total) * 100, 1)},
        ]
        serializer = FunnelStageSerializer(stages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
