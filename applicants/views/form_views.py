"""
Application and Candidate Form Views.
Orchestrates candidate registration, resume ingestion, application management, and pipeline transitions.
Delegates business logic to applicants.services.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction

from ..models import UserData, Document, Application
from jobs.models import Job
from ..services.resume_parser import extract_pdf_text, extract_metadata_from_text
from ..services.skill_service import extract_skills_from_text, sync_candidate_skills
from ..services.matching_service import calculate_ats_match
from ..services.activity_service import log_activity


def form(request):
    """
    Public candidate application / profile update endpoint.
    Processes uploaded PDF resume, extracts skills & experience, calculates ATS match score,
    and binds the candidate to an application if job_id is present.
    """
    if request.method == "POST":
        record_id = request.POST.get("record_id")
        job_id = request.POST.get("job_id")
        uploaded_file = request.FILES.get("myfile")

        if not uploaded_file and not record_id:
            messages.error(request, "Resume upload is required")
            return redirect('contact_form')

        with transaction.atomic():
            # 1. Update Existing Candidate OR Create New Candidate
            if record_id:
                user_data = get_object_or_404(UserData, id=record_id)
                user_data.name = request.POST['name']
                user_data.email = request.POST['email']
                user_data.gender = request.POST['gender']
                user_data.phone_number = request.POST.get('phone_number')
                user_data.country = request.POST['country']
                user_data.cover_letter = request.POST.get('cover_letter')
                user_data.linkedin_url = request.POST.get('linkedin_url')
                user_data.portfolio_url = request.POST.get('portfolio_url')
                user_data.save()

                log_activity(
                    action="Candidate profile updated",
                    candidate=user_data,
                    performed_by=request.user
                )
            else:
                user_data = UserData.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    name=request.POST['name'],
                    email=request.POST['email'],
                    gender=request.POST['gender'],
                    phone_number=request.POST.get('phone_number'),
                    country=request.POST['country'],
                    cover_letter=request.POST.get('cover_letter'),
                    linkedin_url=request.POST.get('linkedin_url'),
                    portfolio_url=request.POST.get('portfolio_url'),
                )

            # 2. Process Resume (if file provided)
            if uploaded_file:
                extracted_text = extract_pdf_text(uploaded_file)
                metadata = extract_metadata_from_text(extracted_text)
                detected_skills = extract_skills_from_text(extracted_text)

                # Synchronize skills with candidate
                sync_candidate_skills(
                    candidate=user_data,
                    detected_skills=detected_skills,
                    skill_experience_map=metadata["skill_experience"]
                )

                # Persist or update Document record
                document = Document.objects.filter(user_data=user_data).first()
                if document:
                    document.file = uploaded_file
                    document.pdf_text = extracted_text
                    document.additional_info = metadata["additional_info"]
                    document.experience_info = metadata["experience_info"]
                    document.save()
                    log_activity(
                        action="Resume replaced and re-parsed",
                        candidate=user_data,
                        performed_by=request.user
                    )
                else:
                    Document.objects.create(
                        user=request.user if request.user.is_authenticated else None,
                        user_data=user_data,
                        file=uploaded_file,
                        pdf_text=extracted_text,
                        additional_info=metadata["additional_info"],
                        experience_info=metadata["experience_info"],
                    )
                    log_activity(
                        action="Resume uploaded and parsed",
                        candidate=user_data,
                        performed_by=request.user
                    )

            # 3. Handle Job Application & ATS Scoring
            target_job = None
            if job_id:
                target_job = Job.objects.filter(id=job_id).first()
            elif record_id:
                # If editing, recalculate score for any existing applications
                existing_app = Application.objects.filter(candidate=user_data).first()
                if existing_app:
                    target_job = existing_app.job

            if target_job:
                match_result = calculate_ats_match(user_data, target_job)
                app, created = Application.objects.update_or_create(
                    candidate=user_data,
                    job=target_job,
                    defaults={"ats_score": match_result["score"]}
                )
                action_text = (
                    f"Applied for '{target_job.title}' with ATS score {match_result['score']}%"
                    if created
                    else f"ATS score recalculated to {match_result['score']}% for '{target_job.title}'"
                )
                log_activity(
                    action=action_text,
                    candidate=user_data,
                    performed_by=request.user
                )

        messages.success(request, "Application submitted successfully" if not record_id else "Data updated successfully")
        return redirect('form_success')

    return render(request, 'FORM.html', {'active_page': 'form'})


@login_required(login_url='login_view')
def applications_list(request):
    """
    Recruiter pipeline applications list view with job and status filtering and score/date sorting.
    """
    applications = Application.objects.select_related('candidate', 'job').order_by('-applied_at')

    selected_job = request.GET.get('job')
    selected_status = request.GET.get('status')
    selected_sort = request.GET.get('sort')

    if selected_job:
        applications = applications.filter(job_id=selected_job)
    if selected_status:
        applications = applications.filter(status=selected_status)

    if selected_sort == 'high_ats':
        applications = applications.order_by('-ats_score')
    elif selected_sort == 'low_ats':
        applications = applications.order_by('ats_score')
    elif selected_sort == 'oldest':
        applications = applications.order_by('applied_at')
    else:
        applications = applications.order_by('-applied_at')

    jobs = Job.objects.filter(is_active=True)

    # Calculate status counts across all applications
    all_apps = Application.objects.all()
    if selected_job:
        all_apps = all_apps.filter(job_id=selected_job)

    total_applications = all_apps.count()
    applied_count = all_apps.filter(status='Applied').count()
    review_count = all_apps.filter(status='Under Review').count()
    shortlisted_count = all_apps.filter(status='Shortlisted').count()
    rejected_count = all_apps.filter(status='Rejected').count()
    hired_count = all_apps.filter(status='Hired').count()

    return render(
        request,
        'applications_list.html',
        {
            'applications': applications,
            'jobs': jobs,
            'selected_job': selected_job,
            'selected_status': selected_status,
            'active_page': 'applications',
            'total_applications': total_applications,
            'applied_count': applied_count,
            'review_count': review_count,
            'shortlisted_count': shortlisted_count,
            'rejected_count': rejected_count,
            'hired_count': hired_count,
            'selected_sort': selected_sort,
        }
    )


@login_required(login_url='login_view')
def update_application_status(request, application_id):
    """
    Updates recruitment stage for an application and logs the transition.
    """
    application = get_object_or_404(Application, id=application_id)

    if request.method == "POST":
        new_status = request.POST.get('status')
        if new_status and new_status != application.status:
            application.status = new_status
            application.save(update_fields=['status'])
            log_activity(
                action=f"Application status changed to '{new_status}' for {application.candidate.name}",
                candidate=application.candidate,
                performed_by=request.user
            )

    return redirect('applications_list')
