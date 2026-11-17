from django.urls import path
from .views import (
    AnalyticsDashboardAPIView,
    SkillsDistributionAPIView,
    ExperienceDistributionAPIView,
    RecruitmentFunnelAPIView,
)

urlpatterns = [
    path('dashboard/', AnalyticsDashboardAPIView.as_view(), name='api_analytics_dashboard'),
    path('skills/', SkillsDistributionAPIView.as_view(), name='api_analytics_skills'),
    path('experience/', ExperienceDistributionAPIView.as_view(), name='api_analytics_experience'),
    path('funnel/', RecruitmentFunnelAPIView.as_view(), name='api_analytics_funnel'),
]
