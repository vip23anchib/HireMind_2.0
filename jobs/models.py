from django.db import models


class Job(models.Model):

    JOB_TYPES = (
        ('Full Time', 'Full Time'),
        ('Internship', 'Internship'),
        ('Contract', 'Contract'),
    )

    title = models.CharField(
        max_length=200
    )

    slug = models.SlugField(
        unique=True
    )

    department = models.CharField(
        max_length=100
    )

    location = models.CharField(
        max_length=100
    )

    job_type = models.CharField(
        max_length=50,
        choices=JOB_TYPES
    )

    description = models.TextField()

    requirements = models.TextField()
    required_skills = models.ManyToManyField(
        'applicants.Skill',
        blank=True
    )

    responsibilities = models.TextField()

    experience_required = models.IntegerField()

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_active', '-created_at'], name='idx_job_active_created'),
            models.Index(fields=['department'], name='idx_job_department'),
        ]

    def __str__(self):
        return self.title
