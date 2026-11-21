"""
Automated Unit and Integration Tests for Applicants Services and Views.
Covers resume parsing, skill extraction, ATS scoring, candidate search, and activity logging.
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from jobs.models import Job
from applicants.models import UserData, Document, Skill, UserSkill, Application, ActivityLog
from applicants.services.activity_service import log_activity
from applicants.services.resume_parser import (
    is_valid_resume,
    extract_email,
    extract_phone,
    extract_experience_text,
    extract_skill_experience,
    extract_metadata_from_text,
)
from applicants.services.skill_service import (
    normalize_skill_name,
    extract_skills_from_text,
    sync_candidate_skills,
)
from applicants.services.matching_service import calculate_ats_match
from applicants.services.search_service import search_candidates_service
from applicants.services.analytics_service import (
    get_dashboard_metrics,
    get_skills_distribution,
    get_experience_distribution,
)


class ActivityLogServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test_recruiter", password="password123")
        self.candidate = UserData.objects.create(name="Jane Doe", email="jane@example.com", gender="Female")

    def test_log_activity_creates_record_properly(self):
        log = log_activity("Screened candidate profile", candidate=self.candidate, performed_by=self.user)
        self.assertEqual(log.action, "Screened candidate profile")
        self.assertEqual(log.candidate, self.candidate)
        self.assertEqual(log.performed_by, self.user)
        self.assertIn("Jane Doe", str(log))

    def test_log_activity_handles_unauthenticated_user(self):
        log = log_activity("System automated task", candidate=self.candidate, performed_by=None)
        self.assertIsNone(log.performed_by)
        self.assertEqual(log.action, "System automated task")


class ResumeParserServiceTest(TestCase):
    def test_is_valid_resume_detection(self):
        valid_cv = "Skills: Python, Django. Experience: 4 years. Education: BS Computer Science. Projects: ATS."
        invalid_doc = "Invoice receipt #404. Total amount due: $500. Thank you for your business."
        self.assertTrue(is_valid_resume(valid_cv, threshold=3))
        self.assertFalse(is_valid_resume(invalid_doc, threshold=3))

    def test_extract_contact_and_experience_regexes(self):
        sample_text = (
            "Contact: alex.dev@hiremind.io or call +1-555-234-5678.\n"
            "Summary: Senior Full-Stack Engineer with 6 years of experience.\n"
            "Skills & Timeline: Python - 5 years, React.js (3 years), Django - 4 years."
        )
        self.assertEqual(extract_email(sample_text), "alex.dev@hiremind.io")
        self.assertIn("555", extract_phone(sample_text))
        self.assertEqual(extract_experience_text(sample_text).lower(), "6 years")

        skill_exp = extract_skill_experience(sample_text)
        self.assertEqual(skill_exp.get("Python"), 5)
        self.assertEqual(skill_exp.get("React.js"), 3)
        self.assertEqual(skill_exp.get("Django"), 4)

    def test_extract_metadata_from_text(self):
        sample_text = "Email: dev@example.com Phone: +919876543210 Experience: 3 years. Python - 3 years."
        meta = extract_metadata_from_text(sample_text)
        self.assertEqual(meta["email"], "dev@example.com")
        self.assertIn("Email: dev@example.com", meta["additional_info"])
        self.assertIn("Python: 3 years", meta["experience_info"])


class SkillServiceTest(TestCase):
    def setUp(self):
        self.candidate = UserData.objects.create(name="Dev User", email="dev@test.com", gender="Male")

    def test_normalize_skill_name(self):
        self.assertEqual(normalize_skill_name("reactjs"), "React.js")
        self.assertEqual(normalize_skill_name("react.js"), "React.js")
        self.assertEqual(normalize_skill_name("drf"), "Django REST Framework")
        self.assertEqual(normalize_skill_name("k8s"), "Kubernetes")
        self.assertEqual(normalize_skill_name("postgres"), "PostgreSQL")

    def test_extract_skills_from_text(self):
        text = "Extensive experience building APIs in Python and Django REST Framework with PostgreSQL and Docker."
        skills = extract_skills_from_text(text)
        self.assertIn("Python", skills)
        self.assertIn("Django REST Framework", skills)
        self.assertIn("PostgreSQL", skills)
        self.assertIn("Docker", skills)

    def test_sync_candidate_skills(self):
        detected = ["Python", "Django", "PostgreSQL"]
        exp_map = {"Python": 4, "Django": 3}
        user_skills = sync_candidate_skills(self.candidate, detected, exp_map)

        self.assertEqual(len(user_skills), 3)
        python_us = UserSkill.objects.get(user_data=self.candidate, skill__name="Python")
        self.assertEqual(python_us.years_of_experience, 4)
        pg_us = UserSkill.objects.get(user_data=self.candidate, skill__name="PostgreSQL")
        self.assertEqual(pg_us.years_of_experience, 0)


class MatchingServiceTest(TestCase):
    def setUp(self):
        self.candidate = UserData.objects.create(name="Alice", email="alice@test.com", gender="Female")
        py_skill = Skill.objects.create(name="Python")
        dj_skill = Skill.objects.create(name="Django")
        react_skill = Skill.objects.create(name="React.js")

        UserSkill.objects.create(user_data=self.candidate, skill=py_skill, years_of_experience=3)
        UserSkill.objects.create(user_data=self.candidate, skill=dj_skill, years_of_experience=2)

        self.job = Job.objects.create(
            title="Backend Python Developer",
            slug="backend-python-developer",
            department="Engineering",
            location="Remote",
            job_type="Full Time",
            experience_required=2
        )
        self.job.required_skills.set([py_skill, dj_skill, react_skill])

    def test_calculate_ats_match_score_and_gaps(self):
        result = calculate_ats_match(self.candidate, self.job)
        # 2 out of 3 matched = 66.67%
        self.assertEqual(result["score"], 66.67)
        self.assertEqual(result["matched_skills"], ["Django", "Python"])
        self.assertEqual(result["missing_skills"], ["React.js"])
        self.assertEqual(result["total_required"], 3)


class SearchServiceTest(TestCase):
    def setUp(self):
        self.cand1 = UserData.objects.create(name="Python Master", email="py@test.com", gender="Male")
        self.cand2 = UserData.objects.create(name="Fullstack Dev", email="fs@test.com", gender="Female")

        s_py = Skill.objects.create(name="Python")
        s_dj = Skill.objects.create(name="Django")
        s_react = Skill.objects.create(name="React.js")

        UserSkill.objects.create(user_data=self.cand1, skill=s_py, years_of_experience=5)
        UserSkill.objects.create(user_data=self.cand2, skill=s_py, years_of_experience=3)
        UserSkill.objects.create(user_data=self.cand2, skill=s_dj, years_of_experience=2)
        UserSkill.objects.create(user_data=self.cand2, skill=s_react, years_of_experience=2)

    def test_or_search_service(self):
        res = search_candidates_service(skill_query="Django, React.js", search_type="or")
        self.assertEqual(res["total_matches"], 1)
        self.assertEqual(res["candidate_results"][0]["candidate"], self.cand2)

    def test_and_search_service(self):
        # Python AND Django: only cand2 has both
        res = search_candidates_service(skill_query="Python, Django", search_type="and")
        self.assertEqual(res["total_matches"], 1)
        self.assertEqual(res["candidate_results"][0]["candidate"], self.cand2)
        self.assertEqual(res["candidate_results"][0]["score"], 100)

    def test_experience_filter(self):
        # Minimum 4 years experience in Python: only cand1 matches
        res = search_candidates_service(skill_query="Python", min_experience=4, search_type="or")
        self.assertEqual(res["total_matches"], 1)
        self.assertEqual(res["candidate_results"][0]["candidate"], self.cand1)


class AnalyticsServiceTest(TestCase):
    def setUp(self):
        cand = UserData.objects.create(name="Bob", email="bob@test.com", gender="Male")
        skill = Skill.objects.create(name="Python")
        UserSkill.objects.create(user_data=cand, skill=skill, years_of_experience=4)
        job = Job.objects.create(title="Dev", slug="dev", experience_required=1)
        Application.objects.create(candidate=cand, job=job, status="Shortlisted", ats_score=85.0)

    def test_analytics_metrics(self):
        metrics = get_dashboard_metrics()
        self.assertEqual(metrics["total_candidates"], 1)
        self.assertEqual(metrics["total_applications"], 1)
        self.assertEqual(metrics["shortlisted"], 1)

        skills = get_skills_distribution()
        self.assertEqual(len(skills), 1)
        self.assertEqual(skills[0]["skill"], "Python")

        exp = get_experience_distribution()
        self.assertEqual(exp[0]["avg_years"], 4.0)


class CeleryResumeProcessingTaskTest(TestCase):
    def setUp(self):
        from unittest.mock import MagicMock
        from django.core.files.uploadedfile import SimpleUploadedFile
        from applicants.tasks import process_resume_task

        self.candidate = UserData.objects.create(name="Task Candidate", email="task@candidate.io")
        self.skill_py = Skill.objects.create(name="Python")
        self.skill_dj = Skill.objects.create(name="Django")
        self.job = Job.objects.create(title="Backend Dev", slug="backend-dev", experience_required=2)
        self.job.required_skills.set([self.skill_py, self.skill_dj])

        self.app = Application.objects.create(
            candidate=self.candidate,
            job=self.job,
            status="Applied",
            ats_score=0.0
        )

        sample_file = SimpleUploadedFile("candidate_resume.pdf", b"%PDF-1.4 dummy resume", content_type="application/pdf")
        self.doc = Document.objects.create(
            user_data=self.candidate,
            file=sample_file,
            status="Queued"
        )

    def test_process_resume_task_success(self):
        from unittest.mock import patch
        from applicants.tasks import process_resume_task

        mock_resume_text = (
            "Alex Task\n"
            "Email: task@candidate.io | Phone: +1 555-0199\n"
            "Professional Experience: 4 years working with Python and Django.\n"
            "Skills: Python, Django, PostgreSQL.\n"
            "Education: BS in Computer Science.\n"
            "Projects: Built automated applicant tracking system."
        )

        with patch("applicants.tasks.extract_pdf_text", return_value=mock_resume_text):
            result = process_resume_task(self.doc.id, application_id=self.app.id)

        self.assertEqual(result["status"], "Completed")
        self.doc.refresh_from_db()
        self.assertEqual(self.doc.status, "Completed")

        # Verify candidate phone updated
        self.candidate.refresh_from_db()
        self.assertIn("555", self.candidate.phone_number)

        # Verify skills synced
        candidate_skills = list(self.candidate.skills_m2m.values_list('name', flat=True))
        self.assertIn("Python", candidate_skills)
        self.assertIn("Django", candidate_skills)

        # Verify application ATS score recalculated
        self.app.refresh_from_db()
        self.assertEqual(self.app.ats_score, 100.0)

    def test_process_resume_task_invalid_document_fails_gracefully(self):
        from unittest.mock import patch
        from applicants.tasks import process_resume_task

        # Return non-resume garbage text
        with patch("applicants.tasks.extract_pdf_text", return_value="Random non-resume grocery list milk eggs bread"):
            result = process_resume_task(self.doc.id)

        self.assertEqual(result["status"], "Failed")
        self.doc.refresh_from_db()
        self.assertEqual(self.doc.status, "Failed")
