"""
Comprehensive Automated Tests for HireMind REST API v1.
Validates authentication, jobs, candidates, applications, resume processing, search, analytics, and OpenAPI documentation.
"""

import io
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from jobs.models import Job
from applicants.models import UserData, Document, Skill, UserSkill, Application, ApplicationStatusHistory
from members.models import Member


class APIRestFrameworkTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Recruiter user
        self.recruiter_user = User.objects.create_user(
            username="recruiter_jane",
            email="jane@hiremind.io",
            password="StrongPassword123!"
        )
        self.member = Member.objects.create(
            user=self.recruiter_user,
            firstname="Jane",
            lastname="Recruiter",
            role="Recruiter"
        )

        # Admin user
        self.admin_user = User.objects.create_superuser(
            username="admin_vip",
            email="admin@hiremind.io",
            password="AdminPassword123!"
        )

        # Test Skills
        self.skill_python = Skill.objects.create(name="Python")
        self.skill_django = Skill.objects.create(name="Django")
        self.skill_react = Skill.objects.create(name="React.js")

        # Test Job
        self.job = Job.objects.create(
            title="Full Stack Python/React Engineer",
            slug="full-stack-python-react-engineer",
            department="Engineering",
            location="Remote",
            job_type="Full Time",
            description="Build scalable web applications",
            requirements="Python, Django, React.js",
            responsibilities="Design APIs and UI",
            experience_required=3,
            is_active=True
        )
        self.job.required_skills.set([self.skill_python, self.skill_django, self.skill_react])

        # Test Candidate
        self.candidate = UserData.objects.create(
            name="Alex Dev",
            email="alex@hiremind.io",
            phone_number="1234567890",
            country="United States"
        )
        UserSkill.objects.create(user_data=self.candidate, skill=self.skill_python, years_of_experience=4)
        UserSkill.objects.create(user_data=self.candidate, skill=self.skill_django, years_of_experience=3)

        # Test Application
        self.application = Application.objects.create(
            candidate=self.candidate,
            job=self.job,
            status="Applied",
            ats_score=66.67
        )

    # -------------------------------------------------------------
    # 1. Authentication Endpoints
    # -------------------------------------------------------------
    def test_login_success_and_failure(self):
        # Invalid credentials
        res = self.client.post(
            reverse('api_auth_login'),
            data={"username": "recruiter_jane", "password": "WrongPassword"},
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['error_code'], 'VALIDATION_ERROR')

        # Valid credentials
        res = self.client.post(
            reverse('api_auth_login'),
            data={"username": "recruiter_jane", "password": "StrongPassword123!"},
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['user']['username'], 'recruiter_jane')
        self.assertEqual(res.json()['user']['role'], 'Recruiter')

    def test_current_user_me_endpoint(self):
        # Unauthenticated
        res = self.client.get(reverse('api_auth_me'))
        self.assertIn(res.status_code, [401, 403])

        # Authenticated
        self.client.force_login(self.recruiter_user)
        res = self.client.get(reverse('api_auth_me'))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['email'], 'jane@hiremind.io')

    def test_logout_endpoint(self):
        self.client.force_login(self.recruiter_user)
        res = self.client.post(reverse('api_auth_logout'))
        self.assertEqual(res.status_code, 200)

        # Follow-up request is now unauthenticated
        res = self.client.get(reverse('api_auth_me'))
        self.assertIn(res.status_code, [401, 403])

    # -------------------------------------------------------------
    # 2. Jobs Endpoints
    # -------------------------------------------------------------
    def test_public_jobs_list(self):
        # Public users can list active jobs
        res = self.client.get('/api/v1/jobs/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['count'], 1)
        self.assertEqual(res.json()['results'][0]['slug'], 'full-stack-python-react-engineer')

    def test_job_create_and_permissions(self):
        job_payload = {
            "title": "Data Scientist",
            "slug": "data-scientist",
            "department": "Data",
            "location": "New York",
            "job_type": "Full Time",
            "description": "Analyze ML models",
            "requirements": "Python, SQL",
            "responsibilities": "Feature engineering",
            "experience_required": 4,
            "is_active": True,
            "required_skill_ids": [self.skill_python.id]
        }
        # Anonymous fails with 401 or 403
        res = self.client.post('/api/v1/jobs/', data=job_payload, content_type="application/json")
        self.assertIn(res.status_code, [401, 403])

        # Recruiter succeeds
        self.client.force_login(self.recruiter_user)
        res = self.client.post('/api/v1/jobs/', data=job_payload, content_type="application/json")
        self.assertEqual(res.status_code, 201)
        self.assertTrue(Job.objects.filter(slug="data-scientist").exists())

    def test_job_toggle_status_and_statistics(self):
        self.client.force_login(self.recruiter_user)

        # Toggle to inactive
        res = self.client.post(f'/api/v1/jobs/{self.job.id}/toggle-status/')
        self.assertEqual(res.status_code, 200)
        self.assertFalse(res.json()['is_active'])

        # Statistics
        res = self.client.get(f'/api/v1/jobs/{self.job.id}/statistics/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['total'], 1)
        self.assertEqual(res.json()['applied'], 1)

    # -------------------------------------------------------------
    # 3. Candidates Endpoints
    # -------------------------------------------------------------
    def test_candidates_list_and_detail(self):
        self.client.force_login(self.recruiter_user)

        res = self.client.get('/api/v1/candidates/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['count'], 1)
        self.assertEqual(res.json()['results'][0]['name'], 'Alex Dev')

        res = self.client.get(f'/api/v1/candidates/{self.candidate.id}/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json()['skills']), 2)

    def test_candidate_resume_download_security(self):
        # Create a sample document
        sample_pdf = SimpleUploadedFile("resume.pdf", b"%PDF-1.4 dummy content", content_type="application/pdf")
        doc = Document.objects.create(
            user_data=self.candidate,
            file=sample_pdf,
            status='Completed'
        )

        # Anonymous cannot download
        res = self.client.get(f'/api/v1/candidates/{self.candidate.id}/resume/')
        self.assertIn(res.status_code, [401, 403])

        # Recruiter can download
        self.client.force_login(self.recruiter_user)
        res = self.client.get(f'/api/v1/candidates/{self.candidate.id}/resume/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res['Content-Type'], 'application/pdf')

    # -------------------------------------------------------------
    # 4. Applications & Pipeline Endpoints
    # -------------------------------------------------------------
    def test_application_status_transition_and_history(self):
        self.client.force_login(self.recruiter_user)

        # Transition status to 'Shortlisted'
        res = self.client.patch(
            f'/api/v1/applications/{self.application.id}/status/',
            data={"status": "Shortlisted", "notes": "Strong Python background."},
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['status'], 'Shortlisted')

        # Check status history endpoint
        res = self.client.get(f'/api/v1/applications/{self.application.id}/history/')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(res.json()) >= 1)
        self.assertEqual(res.json()[0]['new_status'], 'Shortlisted')

    # -------------------------------------------------------------
    # 5. Search & Matching Endpoints
    # -------------------------------------------------------------
    def test_candidate_search_api(self):
        self.client.force_login(self.recruiter_user)

        # Search by single skill
        res = self.client.get('/api/v1/search/candidates/?skill=Python')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['total_matches'], 1)
        self.assertEqual(res.json()['results'][0]['candidate']['name'], 'Alex Dev')

        # Search by skills AND operator
        res = self.client.get('/api/v1/search/candidates/?skill=Python,Django&search_type=and')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['total_matches'], 1)
        self.assertEqual(res.json()['results'][0]['score'], 100)

    def test_candidate_job_match_api(self):
        self.client.force_login(self.recruiter_user)
        res = self.client.get(f'/api/v1/search/matches/?candidate_id={self.candidate.id}&job_id={self.job.id}')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['score'], 66.67)
        self.assertIn('React.js', res.json()['missing_skills'])

    # -------------------------------------------------------------
    # 6. Analytics Endpoints
    # -------------------------------------------------------------
    def test_analytics_endpoints(self):
        self.client.force_login(self.recruiter_user)

        res = self.client.get('/api/v1/analytics/dashboard/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['total_jobs'] if 'total_jobs' in res.json() else res.json()['active_jobs'], 1)

        res = self.client.get('/api/v1/analytics/skills/')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(res.json()) >= 1)

        res = self.client.get('/api/v1/analytics/funnel/')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(res.json()) >= 1)

    # -------------------------------------------------------------
    # 7. OpenAPI Documentation Endpoints
    # -------------------------------------------------------------
    def test_openapi_schema_and_swagger_ui(self):
        # OpenAPI JSON / YAML schema
        res = self.client.get('/api/schema/')
        self.assertEqual(res.status_code, 200)

        # Swagger UI
        res = self.client.get('/api/docs/')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "swagger-ui")

        # Redoc UI
        res = self.client.get('/api/redoc/')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "redoc")

    # -------------------------------------------------------------
    # 8. Asynchronous Resume Ingestion & Status Tracking
    # -------------------------------------------------------------
    def test_resume_upload_and_status_polling(self):
        from unittest.mock import patch
        mock_text = (
            "Alex Resume\n"
            "Email: alex@hiremind.io | Phone: +1 555-9876\n"
            "Experience: 4 years Python developer.\n"
            "Skills: Python, React.js.\n"
            "Education: BS CS\n"
            "Projects: Full stack ATS application."
        )

        sample_pdf = SimpleUploadedFile("test_resume.pdf", b"%PDF-1.4 dummy resume", content_type="application/pdf")

        with patch("applicants.tasks.extract_pdf_text", return_value=mock_text):
            res = self.client.post(
                '/api/v1/resumes/upload/',
                data={
                    'file': sample_pdf,
                    'candidate_id': self.candidate.id
                },
                format='multipart'
            )

        self.assertIn(res.status_code, [201, 202])
        doc_id = res.json()['id']
        self.assertTrue(doc_id > 0)

        # Poll status
        status_res = self.client.get(f'/api/v1/resumes/{doc_id}/status/')
        self.assertEqual(status_res.status_code, 200)
        self.assertIn(status_res.json()['status'], ['Queued', 'Processing', 'Completed'])

    # -------------------------------------------------------------
    # 9. Health Check Endpoint
    # -------------------------------------------------------------
    def test_health_check_endpoint(self):
        res = self.client.get('/api/v1/health/')
        self.assertIn(res.status_code, [200, 503])
        self.assertIn('checks', res.json())
        self.assertEqual(res.json()['checks']['database'], 'healthy')
