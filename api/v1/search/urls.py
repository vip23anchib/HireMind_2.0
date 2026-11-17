from django.urls import path
from .views import CandidateSearchAPIView, CandidateJobMatchAPIView

urlpatterns = [
    path('candidates/', CandidateSearchAPIView.as_view(), name='api_search_candidates'),
    path('matches/', CandidateJobMatchAPIView.as_view(), name='api_search_matches'),
]
