from django.contrib import admin

# Register your models here.
from .models import Job



@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    filter_horizontal = (
        'required_skills',
    )