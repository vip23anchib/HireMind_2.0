"""
Activity Logs API Serializers.
"""

from rest_framework import serializers
from applicants.models import ActivityLog


class ActivityLogSerializer(serializers.ModelSerializer):
    candidate_name = serializers.CharField(source='candidate.name', read_only=True)
    performed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = ActivityLog
        fields = [
            'id',
            'action',
            'candidate',
            'candidate_name',
            'performed_by',
            'performed_by_name',
            'created_at',
        ]

    def get_performed_by_name(self, obj):
        if obj.performed_by:
            return obj.performed_by.get_full_name() or obj.performed_by.username
        return "System"
