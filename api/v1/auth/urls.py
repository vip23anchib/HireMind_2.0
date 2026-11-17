from django.urls import path
from .views import LoginAPIView, LogoutAPIView, CurrentUserAPIView, ChangePasswordAPIView

urlpatterns = [
    path('login/', LoginAPIView.as_view(), name='api_auth_login'),
    path('logout/', LogoutAPIView.as_view(), name='api_auth_logout'),
    path('me/', CurrentUserAPIView.as_view(), name='api_auth_me'),
    path('password/', ChangePasswordAPIView.as_view(), name='api_auth_password'),
]
