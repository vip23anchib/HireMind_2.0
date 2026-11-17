from django.urls import path
from .views import ResumeUploadAPIView, ResumeStatusAPIView

urlpatterns = [
    path('upload/', ResumeUploadAPIView.as_view(), name='api_resumes_upload'),
    path('<int:id>/status/', ResumeStatusAPIView.as_view(), name='api_resumes_status'),
]
