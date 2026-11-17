"""
Authentication API Views.
Provides login, logout, current user session state, and password management.
"""

from rest_framework import status, views, permissions
from rest_framework.response import Response
from django.contrib.auth import login, logout
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .serializers import LoginSerializer, UserProfileSerializer, ChangePasswordSerializer
from applicants.services.activity_service import log_activity


class LoginAPIView(views.APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        request=LoginSerializer,
        responses={
            200: UserProfileSerializer,
            400: OpenApiResponse(description="Validation error / Invalid credentials")
        },
        description="Authenticate recruiter or administrator credentials and initiate session."
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)

        log_activity(
            action=f"User '{user.username}' logged in via API",
            performed_by=user
        )

        return Response({
            "message": "Login successful.",
            "user": UserProfileSerializer(user).data
        }, status=status.HTTP_200_OK)


class LogoutAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=None,
        responses={200: OpenApiResponse(description="Logged out successfully.")},
        description="Terminates recruiter session."
    )
    def post(self, request):
        username = request.user.username
        logout(request)
        return Response({"message": f"Successfully logged out user '{username}'."}, status=status.HTTP_200_OK)


class CurrentUserAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses={200: UserProfileSerializer},
        description="Retrieves the profile and role details of the currently authenticated recruiter."
    )
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChangePasswordAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=ChangePasswordSerializer,
        responses={200: OpenApiResponse(description="Password changed successfully.")},
        description="Updates the authenticated user's password."
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        # Re-login to keep session active after password rotation
        login(request, user)

        log_activity(
            action="Password updated successfully",
            performed_by=user
        )

        return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)
