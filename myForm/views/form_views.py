
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required # Import protection decorator
from ..models import UserData, Document,Skill, UserSkill
from django.contrib import messages
from django.http import JsonResponse
from pypdf import PdfReader
from django.core.paginator import Paginator
import re 

from .form_helper import extract_pdf_text, is_resume, extract_skills
from .form_helper import extract_email, extract_phone, extract_experience,extract_skill_experience


#combined function for both create and update based on whether its GET or POST 
@login_required(login_url='login_view')
def form(request):

    if request.method == "POST":
        skills = request.POST.getlist('skills')

        record_id = request.POST.get("record_id")

        if record_id:
            user_data = UserData.objects.get(id=record_id)

            user_data.name = request.POST['name']
            user_data.email = request.POST['email']
            user_data.gender = request.POST['gender']
            user_data.country = request.POST['country']
            user_data.message = request.POST['message']
            user_data.skills = ", ".join(skills)

            user_data.save()

            new_file = request.FILES.get("myfile")
            if new_file:
                document = Document.objects.filter(
                    user_data=user_data
                ).first()

                if document:
                    extracted_text = extract_pdf_text(new_file)

                    experience_data = extract_skill_experience(
                    extracted_text
                    )
                    print(experience_data)

                    UserSkill.objects.filter(
                        user_data=user_data
                        ).delete()

                    for skill_name, years in experience_data.items():

                        print(
                            "Creating:",
                            skill_name,
                            years
                        )
                        skill, created = Skill.objects.get_or_create(
                            name=skill_name
                        )

                        UserSkill.objects.create(
                            user_data=user_data,
                            skill=skill,
                            years_of_experience=int(years)
                        )

                       
                        print("Saved")

                    formatted_experience = ""
                    for skill, years in experience_data.items():
                        formatted_experience += (
                        f"{skill}: {years} years\n")
                    
                    print(formatted_experience)

                    email = extract_email(extracted_text)
                    phone = extract_phone(extracted_text)
                    experience = extract_experience(extracted_text)
                    additional_info = ""
                    if email:
                        additional_info += f"Email: {email}\n"
                    if phone:
                        additional_info += f"Phone: {phone}\n"
                    if experience:
                        additional_info += f"Experience: {experience}\n"

                    resume_skills = []
                    if is_resume(extracted_text):
                        resume_skills = extract_skills(extracted_text)
                        print("Resume Skills:", resume_skills)
                    
                    all_skills = list(
                        set(skills + resume_skills)
                    )
                   

                    document.file = new_file
                    document.pdf_text = extracted_text
                    document.save()
                    document.additional_info = additional_info
                    document.save()

                    
                    user_data.skills = ", ".join(all_skills)
                    user_data.save()
                    print("Saved Skills:", user_data.skills)


            messages.success(request, "Data updated successfully")

        else:
            user_data = UserData.objects.create(
                user=request.user,
                name=request.POST['name'],
                email=request.POST['email'],
                gender=request.POST['gender'],
                country=request.POST['country'],
                message=request.POST['message'],
                skills=", ".join(skills)
        
            )

            all_skills = skills
            if request.FILES.get('myfile'):
                uploaded_file = request.FILES['myfile']
                extracted_text = extract_pdf_text(
                    uploaded_file
                )

                experience_data = extract_skill_experience(#IMPORTANT EXTRACTION
                    extracted_text
                )
                print(experience_data)

                for skill_name, years in experience_data.items():
                    print(
                        "Creating:",
                        skill_name,
                        years
                    )

                    skill, created = Skill.objects.get_or_create(
                        name=skill_name
                    )

                    UserSkill.objects.create(
                        user_data=user_data,
                        skill=skill,
                        years_of_experience=int(years)
                    )

                    print("Saved")

                formatted_experience = ""
                for skill, years in experience_data.items():
                    formatted_experience += (
                        f"{skill}: {years} years\n")
                    
                print(formatted_experience)

                email = extract_email(extracted_text)
                phone = extract_phone(extracted_text)
                experience = extract_experience(extracted_text)
                additional_info = ""
                if email:
                    additional_info += f"Email: {email}\n"
                if phone:
                    additional_info += f"Phone: {phone}\n"
                if experience:
                    additional_info += f"Experience: {experience}\n"

                resume_skills = []
                if is_resume(extracted_text):
                    resume_skills = extract_skills(extracted_text)
                    print("Resume Skills:", resume_skills)
                    
                all_skills = list(
                        set(skills + resume_skills)
                )
                print("Form Skills:", skills)
                print("Resume Skills:", resume_skills)
                print("All Skills:", all_skills)
                
                Document.objects.create( #creating record in your db 
                    user_data=user_data,
                    file=uploaded_file,
                    pdf_text=extracted_text,
                    additional_info=additional_info,
                    experience_info=formatted_experience
            )
            user_data.skills = ", ".join(all_skills)
            user_data.save()

            messages.success(request, "Data saved successfully")

        return redirect('form_success')

    return render(request, 'FORM.html', {
        'active_page': 'form'
    })
