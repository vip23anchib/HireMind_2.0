
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required # Import protection decorator
from ..models import UserData, Document,Skill, UserSkill, Application
from django.contrib import messages
from django.http import JsonResponse
from pypdf import PdfReader
from django.core.paginator import Paginator
import re 

from .form_helper import extract_pdf_text, is_resume, extract_skills
from .form_helper import extract_email, extract_phone, extract_experience,extract_skill_experience

from jobs.models import Job 
from ..models import Application
from django.shortcuts import render, get_object_or_404

from jobs.models import Job

#combined function for both create and update based on whether its GET or POST 


def form(request):

    if request.method == "POST":

        record_id = request.POST.get("record_id")
        job_id = request.POST.get('job_id')

        if not request.FILES.get('myfile') and not record_id:
            messages.error(
                request,
                "Resume upload is required"
            )
            return redirect('contact_form')

        # -----------------------------
        # UPDATE EXISTING RECORD
        # -----------------------------

        if record_id:

            user_data = UserData.objects.get(id=record_id)

            user_data.name = request.POST['name']
            user_data.email = request.POST['email']
            user_data.gender = request.POST['gender']
            user_data.phone_number = request.POST['phone_number']
            user_data.country = request.POST['country']

            user_data.cover_letter = request.POST.get(
                'cover_letter'
            )

            user_data.linkedin_url = request.POST.get(
                'linkedin_url'
            )

            user_data.portfolio_url = request.POST.get(
                'portfolio_url'
            )
             
            

            user_data.save()

            new_file = request.FILES.get("myfile")

            if new_file:

                document = Document.objects.filter(
                    user_data=user_data
                ).first()

                extracted_text = extract_pdf_text(
                    new_file
                )

                experience_data = extract_skill_experience(
                    extracted_text
                )

                print(experience_data)

                # DELETE OLD SKILLS
                UserSkill.objects.filter(
                    user_data=user_data
                ).delete()

                # CREATE NEW SKILLS
                for skill_name, years in experience_data.items():

                    skill, created = Skill.objects.get_or_create(
                        name=skill_name
                    )

                    UserSkill.objects.create(
                        user_data=user_data,
                        skill=skill,
                        years_of_experience=int(years)
                    )

                # FORMAT EXPERIENCE
                formatted_experience = ""

                for skill, years in experience_data.items():

                    formatted_experience += (
                        f"{skill}: {years} years\n"
                    )

                email = extract_email(extracted_text)

                phone = extract_phone(extracted_text)

                experience = extract_experience(
                    extracted_text
                )

                additional_info = ""

                if email:
                    additional_info += (
                        f"Email: {email}\n"
                    )

                if phone:
                    additional_info += (
                        f"Phone: {phone}\n"
                    )

                if experience:
                    additional_info += (
                        f"Experience: {experience}\n"
                    )

                if document:

                    document.file = new_file

                    document.pdf_text = extracted_text

                    document.additional_info = (
                        additional_info
                    )

                    document.experience_info = (
                        formatted_experience
                    )

                    document.save()

            messages.success(
                request,
                "Data updated successfully"
            )

        # -----------------------------
        # CREATE NEW RECORD
        # -----------------------------

        else:

            user_data = UserData.objects.create(

                name=request.POST['name'],

                email=request.POST['email'],

                gender=request.POST['gender'],

                phone_number=request.POST['phone_number'],

                country=request.POST['country'],

                cover_letter=request.POST.get(
                    'cover_letter'
                ),

                linkedin_url=request.POST.get(
                    'linkedin_url'
                ),

                portfolio_url=request.POST.get(
                    'portfolio_url'
                ),
                user=request.user if request.user.is_authenticated else None
            )

            uploaded_file = request.FILES.get(
                'myfile'
            )

            extracted_text = extract_pdf_text(
                uploaded_file
            )

            experience_data = extract_skill_experience(
                extracted_text
            )

            print(experience_data)

            for skill_name, years in experience_data.items():

                skill, created = Skill.objects.get_or_create(
                    name=skill_name
                )

                UserSkill.objects.create(
                    user_data=user_data,
                    skill=skill,
                    years_of_experience=int(years)
                )

            formatted_experience = ""

            for skill, years in experience_data.items():

                formatted_experience += (
                    f"{skill}: {years} years\n"
                )

            email = extract_email(extracted_text)

            phone = extract_phone(extracted_text)

            experience = extract_experience(
                extracted_text
            )

            additional_info = ""

            if email:
                additional_info += (
                    f"Email: {email}\n"
                )

            if phone:
                additional_info += (
                    f"Phone: {phone}\n"
                )

            if experience:
                additional_info += (
                    f"Experience: {experience}\n"
                )

            Document.objects.create(

                user=request.user if request.user.is_authenticated else None,

                user_data=user_data,

                file=uploaded_file,

                pdf_text=extracted_text,

                additional_info=additional_info,

                experience_info=formatted_experience
            )

         #IF candidate applied through careers page
            if job_id:

                job = Job.objects.get(
                    id=job_id
                )


            #to calculate ATS Score we need candidate skills and required job skills
                candidate_skills = set(
                UserSkill.objects.filter(
                    user_data=user_data
                ).values_list(
                    'skill__name',
                    flat=True
                    )
                )
             

                job_skills = set(
                job.required_skills.values_list(
                    'name',
                    flat=True
                    )
                )

                matched_skills = (
                    candidate_skills &
                    job_skills
                )
          

                if len(job_skills) > 0:

                    ats_score = round(
                        (
                            len(matched_skills)
                            /
                            len(job_skills)
                        ) * 100,
                        2
                    )

                else:

                    ats_score = 0

                print("Candidate Skills:", candidate_skills)
                print("Job Skills:", job_skills)
                print("Matched Skills:", matched_skills)
                print("ATS Score:", ats_score)

                Application.objects.create(

                    candidate=user_data,

                    job=job,

                    ats_score = ats_score,
                )

                



            messages.success(
                request,
                "Application submitted successfully"
            )

        return redirect('form_success')

    return render(request, 'FORM.html', {
        'active_page': 'form'
    })



#--------------------------------------------------------------------------------------------------
# application 
@login_required(login_url='login_view')
def applications_list(request):

    applications = Application.objects.select_related(
        'candidate',
        'job'
    ).order_by('-applied_at')

    selected_job = request.GET.get(
        'job'
    )
    selected_status = request.GET.get(
        'status'
    )
    selected_sort = request.GET.get(
    'sort'
    )

    if selected_job:

        applications = applications.filter(
            job_id=selected_job
        )
    if selected_status:

        applications = applications.filter(
            status=selected_status
        )


    jobs = Job.objects.filter(
        is_active=True
    )

#for ordering by the ATS SCORE
    if selected_sort == 'high_ats':

        applications = applications.order_by(
            '-ats_score'
        )

    elif selected_sort == 'low_ats':

        applications = applications.order_by(
            'ats_score'
        )

    elif selected_sort == 'oldest':

        applications = applications.order_by(
            'applied_at'
        )

    else:

        applications = applications.order_by(
            '-applied_at'
        )

#for cards 
    total_applications = applications.count()

    applied_count = applications.filter(
        status='Applied'
    ).count()

    review_count = applications.filter(
        status='Under Review'
    ).count()

    shortlisted_count = applications.filter(
        status='Shortlisted'
    ).count()

    rejected_count = applications.filter(
        status='Rejected'
    ).count()

    hired_count = applications.filter(
        status='Hired'
    ).count()
    
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


#--------------------------------------------------------------------------------------------------
# update application status 

@login_required(login_url='login_view')
def update_application_status(
    request,
    application_id
):

    application = get_object_or_404(
        Application,
        id=application_id
    )

    if request.method == "POST":

        application.status = request.POST.get(
            'status'
        )

        application.save()

    return redirect(
        'applications_list'
    )