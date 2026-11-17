from django.urls import path
from .views import MemberListCreateAPIView

urlpatterns = [
    path('', MemberListCreateAPIView.as_view(), name='api_members_list_create'),
]
