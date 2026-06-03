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

    name = models.CharField(max_length=100)
    email = models.EmailField()
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
        ordering = ['id']  # <-- This tells Django to always sort by ID automatically

    def __str__(self):
        return self.name


class Document(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    user_data = models.ForeignKey(
        UserData,    #Document belongs to a UserData record.
        on_delete=models.CASCADE,
        null=True,
        blank=True
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


    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

#skill table for many to many relationship with Userdata table
class Skill(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    def __str__(self):
        return self.name


#userSkills through table M2M
class UserSkill(models.Model):

    user_data = models.ForeignKey(
        UserData,
        on_delete=models.CASCADE
    )

    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE
    )

    years_of_experience = models.IntegerField(
        null=True,
        blank=True
    )

    def __str__(self):
        return (
            f"{self.user_data.name}"
            f" - "
            f"{self.skill.name}"
        )
    class Meta:
        unique_together = (
            'user_data',
            'skill'
    )



class Application(models.Model):

    STATUS_CHOICES = [

        ('Applied', 'Applied'),

        ('Under Review', 'Under Review'),

        ('Shortlisted', 'Shortlisted'),

        ('Interview Scheduled', 'Interview Scheduled'),

        ('Rejected', 'Rejected'),

        ('Hired', 'Hired'),

    ]

    candidate = models.ForeignKey(  #Means: many applications can belong to one candidate

        UserData,

        on_delete=models.CASCADE,

        related_name='applications'

    )

    job = models.ForeignKey( #Means: many applications can belong to one job

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

        default=0

    )

    applied_at = models.DateTimeField(

        auto_now_add=True

    )

    def __str__(self):

        return f"{self.candidate.name} - {self.job.title}"



