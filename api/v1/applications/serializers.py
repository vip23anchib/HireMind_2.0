"""
Applications API Serializers.
"""

from rest_framework import serializers
from applicants.models import Application, ApplicationStatusHistory, UserData
from jobs.models import Job
from common.permissions import IsRecruiterOrAdmin


class ApplicationStatusHistorySerializer(serializers.ModelSerializer):
    changed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = ApplicationStatusHistory
        fields = [
            'id',
            'old_status',
            'new_status',
            'changed_by',
            'changed_by_name',
            'notes',
            'changed_at',
        ]

    def get_changed_by_name(self, obj):
        if obj.changed_by:
            return obj.changed_by.get_full_name() or obj.changed_by.username
        return "System"


class CandidateSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserData
        fields = [
            'id',
            'name',
            'email',
            'phone_number',
            'country',
        ]


class JobSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = [
            'id',
            'title',
            'slug',
            'department',
            'location',
            'is_active',
        ]


class ApplicationListSerializer(serializers.ModelSerializer):
    candidate = CandidateSummarySerializer(read_only=True)
    job = JobSummarySerializer(read_only=True)

    class Meta:
        model = Application
        fields = [
            'id',
            'candidate',
            'job',
            'status',
            'ats_score',
            'applied_at',
        ]


class ApplicationDetailSerializer(serializers.ModelSerializer):
    candidate = serializers.SerializerMethodField()
    job = JobSummarySerializer(read_only=True)
    status_history = ApplicationStatusHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Application
        fields = [
            'id',
            'candidate',
            'job',
            'status',
            'ats_score',
            'applied_at',
            'status_history',
        ]

    def get_candidate(self, obj):
        from api.v1.candidates.serializers import CandidateDetailSerializer
        return CandidateDetailSerializer(obj.candidate, context=self.context).data


class ApplicationStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Application.STATUS_CHOICES)
    notes = serializers.CharField(required=False, allow_blank=True)


class ApplicationCreateSerializer(serializers.Serializer):
    job_id = serializers.IntegerField(required=True)
    name = serializers.CharField(max_length=100, required=True)
    email = serializers.EmailField(required=True)
    gender = serializers.CharField(max_length=20, required=False, default="Not Specified")
    phone_number = serializers.CharField(max_length=15, required=False, allow_blank=True)
    country = serializers.CharField(max_length=100, required=False, default="Global")
    cover_letter = serializers.CharField(required=False, allow_blank=True)
    linkedin_url = serializers.URLField(required=False, allow_blank=True)
    portfolio_url = serializers.URLField(required=False, allow_blank=True)
    resume_file = serializers.FileField(required=True)

    def validate_job_id(self, value):
        if not Job.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError("Active job with specified ID does not exist.")
        return value
