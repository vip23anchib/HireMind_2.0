from django.contrib import admin

# Register your models here.
from .models import UserData
from .models import Document
from .models import Skill
from .models import UserSkill
admin.site.register(UserData)
admin.site.register(Document)
admin.site.register(Skill)
admin.site.register(UserSkill)