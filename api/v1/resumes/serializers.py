"""
Resumes API Serializers.
"""

from rest_framework import serializers
from applicants.models import Document, UserData
from jobs.models import Job


class ResumeUploadSerializer(serializers.Serializer):
    file = serializers.FileField(required=True)
    candidate_id = serializers.IntegerField(required=False, allow_null=True)
    job_id = serializers.IntegerField(required=False, allow_null=True)

    def validate_file(self, value):
        if not value.name.lower().endswith('.pdf'):
            raise serializers.ValidationError("Only PDF files are supported.")
        # 5MB size limit
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("File size must not exceed 5MB.")
        return value


class ResumeStatusSerializer(serializers.ModelSerializer):
    candidate_name = serializers.CharField(source='user_data.name', read_only=True)
    file_name = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            'id',
            'status',
            'error_message',
            'candidate_name',
            'file_name',
            'uploaded_at',
        ]

    def get_file_name(self, obj):
        return obj.file.name if obj.file else None
