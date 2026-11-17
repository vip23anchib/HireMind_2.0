"""
Search and Matching API Serializers.
"""

from rest_framework import serializers
from applicants.models import UserData


class SearchCandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserData
        fields = [
            'id',
            'name',
            'email',
            'phone_number',
            'country',
        ]


class CandidateSearchResultItemSerializer(serializers.Serializer):
    candidate = SearchCandidateSerializer()
    skills = serializers.ListField(child=serializers.CharField())
    experience = serializers.IntegerField()
    score = serializers.FloatField()
    missing_skills = serializers.ListField(child=serializers.CharField())


class CandidateSearchResponseSerializer(serializers.Serializer):
    total_matches = serializers.IntegerField()
    execution_time_seconds = serializers.FloatField()
    skills_list = serializers.ListField(child=serializers.CharField())
    search_type = serializers.CharField()
    min_experience = serializers.IntegerField(allow_null=True)
    results = CandidateSearchResultItemSerializer(many=True, source='candidate_results')


class CandidateJobMatchResponseSerializer(serializers.Serializer):
    score = serializers.FloatField()
    matched_skills = serializers.ListField(child=serializers.CharField())
    missing_skills = serializers.ListField(child=serializers.CharField())
    candidate_skills = serializers.ListField(child=serializers.CharField())
    required_skills = serializers.ListField(child=serializers.CharField())
    total_required = serializers.IntegerField()
    total_matched = serializers.IntegerField()
