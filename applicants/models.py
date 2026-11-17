from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from jobs.models import Job


class UserData(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    name = models.CharField(
        max_length=100,
        db_index=True
    )
    email = models.EmailField(db_index=True)
    gender = models.CharField(max_length=20)
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )
    country = models.CharField(max_length=100)
    cover_letter = models.TextField(
        blank=True,
        null=True
    )
    linkedin_url = models.URLField(
        blank=True,
        null=True
    )
    portfolio_url = models.URLField(
        blank=True,
        null=True
    )

    skills_m2m = models.ManyToManyField(
        'Skill',
        through='UserSkill',
        blank=True
    )

    class Meta:
        ordering = ['id']
        indexes = [
            models.Index(fields=['name'], name='idx_userdata_name'),
            models.Index(fields=['email'], name='idx_userdata_email'),
        ]

    def __str__(self):
        return self.name


class Document(models.Model):
    STATUS_CHOICES = [
        ('Uploaded', 'Uploaded'),
        ('Queued', 'Queued'),
        ('Processing', 'Processing'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    user_data = models.ForeignKey(
        UserData,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='documents'
    )
    pdf_text = models.TextField(
        blank=True,
        null=True
    )
    additional_info = models.TextField(
        blank=True,
        null=True
    )
    experience_info = models.TextField(
        blank=True,
        null=True
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Completed'
    )
    error_message = models.TextField(
        blank=True,
        null=True
    )
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['status'], name='idx_doc_status'),
            models.Index(fields=['-uploaded_at'], name='idx_doc_uploaded'),
        ]

    def __str__(self):
        owner = self.user_data.name if self.user_data else (self.user.username if self.user else "Anonymous")
        return f"Resume ({self.status}) - {owner}"


class Skill(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class UserSkill(models.Model):
    user_data = models.ForeignKey(
        UserData,
        on_delete=models.CASCADE,
        related_name='user_skills'
    )
    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name='candidate_skills'
    )
    years_of_experience = models.IntegerField(
        null=True,
        blank=True,
        default=0
    )

    class Meta:
        unique_together = ('user_data', 'skill')
        indexes = [
            models.Index(fields=['years_of_experience'], name='idx_userskill_exp'),
        ]

    def __str__(self):
        return f"{self.user_data.name} - {self.skill.name} ({self.years_of_experience} yrs)"


class Application(models.Model):
    STATUS_CHOICES = [
        ('Applied', 'Applied'),
        ('Under Review', 'Under Review'),
        ('Shortlisted', 'Shortlisted'),
        ('Interview Scheduled', 'Interview Scheduled'),
        ('Offer', 'Offer'),
        ('Hired', 'Hired'),
        ('Rejected', 'Rejected'),
        ('Withdrawn', 'Withdrawn'),
    ]

    candidate = models.ForeignKey(
        UserData,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='Applied'
    )
    ats_score = models.FloatField(
        default=0.0
    )
    applied_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ['-applied_at']
        indexes = [
            models.Index(fields=['status'], name='idx_app_status'),
            models.Index(fields=['-applied_at'], name='idx_app_applied'),
            models.Index(fields=['-ats_score'], name='idx_app_ats_score'),
            models.Index(fields=['job', 'status'], name='idx_app_job_status'),
        ]

    def __str__(self):
        return f"{self.candidate.name} - {self.job.title} [{self.status}]"


class ApplicationStatusHistory(models.Model):
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='status_history'
    )
    old_status = models.CharField(max_length=50)
    new_status = models.CharField(max_length=50)
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    notes = models.TextField(blank=True, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-changed_at']
        indexes = [
            models.Index(fields=['application', '-changed_at'], name='idx_app_hist_app_date'),
        ]

    def __str__(self):
        return f"{self.application.candidate.name} ({self.old_status} -> {self.new_status})"


class ActivityLog(models.Model):
    candidate = models.ForeignKey(
        UserData,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    performed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    action = models.CharField(
        max_length=255
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at'], name='idx_actlog_created'),
        ]

    def __str__(self):
        candidate_name = self.candidate.name if self.candidate else "No Candidate"
        return f"{candidate_name} - {self.action}"
