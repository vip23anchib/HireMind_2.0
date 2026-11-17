"""
Members API Views.
Handles recruiter roster listing and team member onboarding.
"""

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from members.models import Member
from common.permissions import IsRecruiterOrAdmin, IsAdminUserRole
from .serializers import MemberSerializer, MemberCreateSerializer


class MemberListCreateAPIView(generics.ListCreateAPIView):
    queryset = Member.objects.select_related('user').all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MemberCreateSerializer
        return MemberSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUserRole()]
        return [IsRecruiterOrAdmin()]

    @extend_schema(
        description="List all internal recruitment and HR team members."
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        request=MemberCreateSerializer,
        responses={201: MemberSerializer},
        description="Onboard a new internal team member with user credentials and assigned role (Admin only)."
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        member = serializer.save()
        return Response(MemberSerializer(member).data, status=status.HTTP_201_CREATED)
