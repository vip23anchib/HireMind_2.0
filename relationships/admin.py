from django.contrib import admin

from .models import *

admin.site.register(Author)
admin.site.register(Book)

admin.site.register(Profile)

admin.site.register(Student)
admin.site.register(Course)

admin.site.register(Trainee)
admin.site.register(TrainingCourse)
admin.site.register(Enrollment)