from django.db import models
from django.contrib.auth.models import User


# =====================================
# ONE TO MANY
# =====================================

class Author(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=100)

    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        related_name='books'
    )

    def __str__(self):
        return self.title


# =====================================
# ONE TO ONE
# =====================================

class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    bio = models.TextField()

    def __str__(self):
        return self.user.username


# =====================================
# MANY TO MANY
# =====================================

class Course(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Student(models.Model):
    name = models.CharField(max_length=100)

    courses = models.ManyToManyField(
        Course,
        related_name='students',
        blank=True
    )

    def __str__(self):
        return self.name


# =====================================
# MANY TO MANY WITH THROUGH
# =====================================

class TrainingCourse(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Trainee(models.Model):
    name = models.CharField(max_length=100)

    courses = models.ManyToManyField(
        TrainingCourse,
        through='Enrollment'
    )

    def __str__(self):
        return self.name


class Enrollment(models.Model):

    trainee = models.ForeignKey(
        Trainee,
        on_delete=models.CASCADE
    )

    course = models.ForeignKey(
        TrainingCourse,
        on_delete=models.CASCADE
    )

    joined_date = models.DateField()

    grade = models.CharField(
        max_length=20
    )

    remarks = models.TextField()

    def __str__(self):
        return f"{self.trainee.name} - {self.course.name}"