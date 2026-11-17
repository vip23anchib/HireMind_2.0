"""
Jobs API Serializers.
"""

from rest_framework import serializers
from jobs.models import Job
from applicants.models import Skill
from jobs.services.job_service import create_job, update_job, get_job_pipeline_stats


class SkillSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name']


class JobSerializer(serializers.ModelSerializer):
    required_skills = SkillSimpleSerializer(many=True, read_only=True)
    required_skill_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Skill.objects.all(),
        write_only=True,
        required=False,
        source='required_skills'
    )
    applications_count = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = [
            'id',
            'title',
            'slug',
            'department',
            'location',
            'job_type',
            'description',
            'requirements',
            'responsibilities',
            'experience_required',
            'is_active',
            'created_at',
            'required_skills',
            'required_skill_ids',
            'applications_count',
        ]
        read_only_fields = ['id', 'created_at']

    def get_applications_count(self, obj):
        return obj.applications.count()

    def create(self, validated_data):
        user = self.context['request'].user if 'request' in self.context else None
        required_skills = validated_data.pop('required_skills', [])
        job = create_job(data=validated_data, performed_by=user)
        if required_skills:
            job.required_skills.set(required_skills)
        return job

    def update(self, instance, validated_data):
        user = self.context['request'].user if 'request' in self.context else None
        required_skills = validated_data.pop('required_skills', None)
        job = update_job(job=instance, data=validated_data, performed_by=user)
        if required_skills is not None:
            job.required_skills.set(required_skills)
        return job


class JobListSerializer(serializers.ModelSerializer):
    applications_count = serializers.SerializerMethodField()
    required_skills = SkillSimpleSerializer(many=True, read_only=True)

    class Meta:
        model = Job
        fields = [
            'id',
            'title',
            'slug',
            'department',
            'location',
            'job_type',
            'experience_required',
            'is_active',
            'created_at',
            'applications_count',
            'required_skills',
        ]

    def get_applications_count(self, obj):
        return obj.applications.count()


class JobStatisticsSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    applied = serializers.IntegerField()
    under_review = serializers.IntegerField()
    shortlisted = serializers.IntegerField()
    interview_scheduled = serializers.IntegerField()
    rejected = serializers.IntegerField()
    hired = serializers.IntegerField()
