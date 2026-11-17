"""
Members API Serializers.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from django.db import transaction

from members.models import Member
from applicants.services.activity_service import log_activity


class MemberSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Member
        fields = [
            'id',
            'firstname',
            'lastname',
            'middlename',
            'phone',
            'joined_date',
            'role',
            'username',
            'email',
        ]


class MemberCreateSerializer(serializers.Serializer):
    firstname = serializers.CharField(max_length=255, required=True)
    lastname = serializers.CharField(max_length=255, required=True)
    middlename = serializers.CharField(max_length=255, required=False, allow_blank=True)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    joined_date = serializers.DateField(required=False, allow_null=True)
    role = serializers.ChoiceField(choices=Member.ROLE_CHOICES, default='Recruiter')
    username = serializers.CharField(max_length=150, required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True, min_length=8)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        username = validated_data.pop('username')
        email = validated_data.pop('email')
        password = validated_data.pop('password')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=validated_data.get('firstname', ''),
            last_name=validated_data.get('lastname', '')
        )

        member = Member.objects.create(
            user=user,
            firstname=validated_data['firstname'],
            lastname=validated_data['lastname'],
            middlename=validated_data.get('middlename', ''),
            phone=validated_data.get('phone', ''),
            joined_date=validated_data.get('joined_date'),
            role=validated_data.get('role', 'Recruiter')
        )

        request = self.context.get('request')
        performed_by = request.user if (request and request.user.is_authenticated) else None

        log_activity(
            action=f"Onboarded team member '{member.firstname} {member.lastname}' as {member.role}",
            performed_by=performed_by
        )

        return member
