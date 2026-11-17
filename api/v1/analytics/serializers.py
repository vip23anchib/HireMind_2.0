"""
Analytics API Serializers.
"""

from rest_framework import serializers


class AnalyticsDashboardSerializer(serializers.Serializer):
    total_applications = serializers.IntegerField()
    active_jobs = serializers.IntegerField()
    total_candidates = serializers.IntegerField()
    total_skills = serializers.IntegerField()
    total_user_skills = serializers.IntegerField()

    applied = serializers.IntegerField()
    under_review = serializers.IntegerField()
    shortlisted = serializers.IntegerField()
    interviews = serializers.IntegerField()
    hired = serializers.IntegerField()
    rejected = serializers.IntegerField()


class SkillDistributionItemSerializer(serializers.Serializer):
    skill = serializers.CharField()
    total = serializers.IntegerField()


class ExperienceDistributionItemSerializer(serializers.Serializer):
    skill = serializers.CharField()
    avg_years = serializers.FloatField()


class FunnelStageSerializer(serializers.Serializer):
    stage = serializers.CharField()
    count = serializers.IntegerField()
    percentage_of_total = serializers.FloatField()
