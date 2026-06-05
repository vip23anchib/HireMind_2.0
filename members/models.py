from django.db import models
from django.contrib.auth.models import User


class Member(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    middlename = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    phone = models.CharField(
        max_length=20,
        null=True,
        blank=True
    )

    joined_date = models.DateField(null=True)

    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('HR Manager', 'HR Manager'),
        ('Recruiter', 'Recruiter'),
    ]

    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='Recruiter'
    )

    def __str__(self):
        return f"{self.firstname} {self.lastname}"