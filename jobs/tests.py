"""
Automated Unit and Integration Tests for Jobs Services and Views.
Covers job vacancy creation, editing, activation toggling, and pipeline statistics.
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from jobs.models import Job
from jobs.services.job_service import (
    create_job,
    update_job,
    toggle_job_status,
    get_job_pipeline_stats,
)
from applicants.models import ActivityLog, UserData, Application


class JobServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="recruiter_rob", password="robpassword")

    def test_create_job_service_and_logging(self):
        data = {
            "title": "Senior DevOps Engineer",
            "department": "Platform",
            "location": "Remote",
            "job_type": "Full Time",
            "description": "Manage Kubernetes clusters",
            "requirements": "Docker, K8s, AWS",
            "responsibilities": "Uptime",
            "experience_required": 5,
        }
        job = create_job(data=data, performed_by=self.user)
        self.assertEqual(job.title, "Senior DevOps Engineer")
        self.assertEqual(job.slug, "senior-devops-engineer")
        self.assertTrue(job.is_active)

        # Check activity log created
        log = ActivityLog.objects.filter(action__icontains="Senior DevOps Engineer").first()
        self.assertIsNotNone(log)
        self.assertEqual(log.performed_by, self.user)

    def test_update_job_service(self):
        job = Job.objects.create(
            title="Junior QA",
            slug="junior-qa",
            department="QA",
            location="Onsite",
            job_type="Contract",
            experience_required=1,
            is_active=True
        )
        updated = update_job(job=job, data={"title": "Lead QA Engineer", "experience_required": 4}, performed_by=self.user)
        self.assertEqual(updated.title, "Lead QA Engineer")
        self.assertEqual(updated.experience_required, 4)

    def test_toggle_job_status_service(self):
        job = Job.objects.create(
            title="SecOps Engineer",
            slug="secops-engineer",
            experience_required=3,
            is_active=True
        )
        new_status = toggle_job_status(job, performed_by=self.user)
        self.assertFalse(new_status)
        self.assertFalse(job.is_active)

        new_status = toggle_job_status(job, performed_by=self.user)
        self.assertTrue(new_status)
        self.assertTrue(job.is_active)

    def test_job_pipeline_stats(self):
        job = Job.objects.create(title="Designer", slug="designer", experience_required=2)
        c1 = UserData.objects.create(name="C1", email="c1@test.com")
        c2 = UserData.objects.create(name="C2", email="c2@test.com")

        Application.objects.create(candidate=c1, job=job, status="Applied")
        Application.objects.create(candidate=c2, job=job, status="Hired")

        stats = get_job_pipeline_stats(job)
        self.assertEqual(stats["total"], 2)
        self.assertEqual(stats["applied"], 1)
        self.assertEqual(stats["hired"], 1)
        self.assertEqual(stats["shortlisted"], 0)


class JobViewsIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="hr_admin", password="securepassword123")
        self.client.force_login(self.user)

    def test_careers_page_renders_active_jobs(self):
        Job.objects.create(title="Active Role", slug="active-role", is_active=True, experience_required=1)
        Job.objects.create(title="Inactive Role", slug="inactive-role", is_active=False, experience_required=1)

        response = self.client.get(reverse('careers'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Active Role")
        self.assertNotContains(response, "Inactive Role")

    def test_create_job_view_post(self):
        post_data = {
            "title": "Machine Learning Engineer",
            "slug": "ml-engineer",
            "department": "AI Labs",
            "location": "Hybrid",
            "job_type": "Full Time",
            "description": "Develop ML pipelines",
            "requirements": "PyTorch, Python",
            "responsibilities": "Training models",
            "experience_required": 3,
        }
        response = self.client.post(reverse('create_job'), data=post_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Job.objects.filter(slug="ml-engineer").exists())
