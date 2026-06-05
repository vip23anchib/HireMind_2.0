from django.contrib import admin

# Register your models here.
from .models import UserData
from .models import Document
from .models import Skill
from .models import UserSkill
from .models import Application
from .models import ActivityLog



admin.site.register(UserData)
admin.site.register(Document)
admin.site.register(Skill)
admin.site.register(UserSkill)
admin.site.register(Application)

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):

    list_display = (
        'candidate',
        'performed_by',
        'action',
        'created_at'
    )