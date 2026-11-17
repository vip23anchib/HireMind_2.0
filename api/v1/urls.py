"""
API v1 Central Router.
Aggregates all version 1 domain API routes.
"""

from django.urls import path, include

urlpatterns = [
    path('auth/', include('api.v1.auth.urls')),
    path('jobs/', include('api.v1.jobs.urls')),
    path('candidates/', include('api.v1.candidates.urls')),
    path('applications/', include('api.v1.applications.urls')),
    path('resumes/', include('api.v1.resumes.urls')),
    path('search/', include('api.v1.search.urls')),
    path('analytics/', include('api.v1.analytics.urls')),
    path('activity-logs/', include('api.v1.activity_logs.urls')),
    path('members/', include('api.v1.members.urls')),
]
