"""
Candidates API Serializers.
"""

from rest_framework import serializers
from applicants.models import UserData, UserSkill, Skill, Document, Application


class CandidateSkillSerializer(serializers.ModelSerializer):
    skill_name = serializers.CharField(source='skill.name', read_only=True)

    class Meta:
        model = UserSkill
        fields = [
            'id',
            'skill_name',
            'years_of_experience',
        ]


class CandidateDocumentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            'id',
            'status',
            'file_url',
            'additional_info',
            'experience_info',
            'uploaded_at',
        ]

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return obj.file.url if obj.file else None


class CandidateListSerializer(serializers.ModelSerializer):
    skills = serializers.SerializerMethodField()
    current_status = serializers.SerializerMethodField()
    latest_ats_score = serializers.SerializerMethodField()
    latest_job_title = serializers.SerializerMethodField()

    class Meta:
        model = UserData
        fields = [
            'id',
            'name',
            'email',
            'gender',
            'phone_number',
            'country',
            'skills',
            'current_status',
            'latest_ats_score',
            'latest_job_title',
        ]

    def get_skills(self, obj):
        return [
            {"skill": us.skill.name, "years": us.years_of_experience or 0}
            for us in obj.user_skills.all()
        ]

    def get_current_status(self, obj):
        apps = list(obj.applications.all())
        return apps[0].status if apps else "N/A"

    def get_latest_ats_score(self, obj):
        apps = list(obj.applications.all())
        return apps[0].ats_score if apps else None

    def get_latest_job_title(self, obj):
        apps = list(obj.applications.all())
        return apps[0].job.title if apps else None


class CandidateDetailSerializer(serializers.ModelSerializer):
    skills = CandidateSkillSerializer(source='user_skills', many=True, read_only=True)
    documents = CandidateDocumentSerializer(many=True, read_only=True)
    applications = serializers.SerializerMethodField()

    class Meta:
        model = UserData
        fields = [
            'id',
            'name',
            'email',
            'gender',
            'phone_number',
            'country',
            'cover_letter',
            'linkedin_url',
            'portfolio_url',
            'skills',
            'documents',
            'applications',
        ]

    def get_applications(self, obj):
        from api.v1.applications.serializers import ApplicationListSerializer
        return ApplicationListSerializer(obj.applications.all(), many=True).data


class CandidateCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserData
        fields = [
            'id',
            'name',
            'email',
            'gender',
            'phone_number',
            'country',
            'cover_letter',
            'linkedin_url',
            'portfolio_url',
        ]
