
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Avg

from jobs.models import Job
from ..models import UserData, Document, UserSkill, Skill, Application, ActivityLog
from ..services.search_service import search_candidates_service
from ..services.analytics_service import (
    get_dashboard_metrics,
    get_skills_distribution,
    get_experience_distribution,
    build_plotly_charts,
)

'''
@login_required(login_url='login_view')
def upload_file(request):

    if request.method == 'POST' and request.FILES.get('myfile'):

        file = request.FILES['myfile']

        if not file.name.endswith('.pdf'):
            return JsonResponse({"error": "Only PDF files allowed"}, status=400)

        # 🔥 get user_data_id from request
        user_data_id = request.POST.get("user_data_id")

        user_data = UserData.objects.get(id=user_data_id)

        Document.objects.create(
            user_data=user_data,
            file=file
        )

        return JsonResponse({"message": "File uploaded successfully"})

    return JsonResponse({"error": "Invalid request"}, status=400)
'''

@login_required(login_url='login_view')
def home_page(request):
    metrics = get_dashboard_metrics()
    context = {
        'total_applications': metrics['total_applications'],
        'active_jobs': metrics['active_jobs'],
        'total_candidates': metrics['total_candidates'],
        'shortlisted': metrics['shortlisted'],
        'interviews': metrics['interviews'],
        'hired': metrics['hired'],
        'recent_applications': metrics['recent_applications'],
    }
    return render(request, "hr_homePage.html", context)



   # 3. Create a simple view for your success page
def success_view(request):
    return render(request, 'success.html')


# ---  NEW LOGIN VIEW ---
def login_view(request):
    if request.method == 'POST':
        # Extract credentials from the POST request body
        user_input = request.POST.get('username')
        pass_input = request.POST.get('password')

        # Django checks these credentials securely against the database user accounts
        user = authenticate(request, username=user_input, password=pass_input)

        if user is not None:
            login(request, user)  # Creates the secure session for the user
            return redirect('home-page')  # Redirects to your data entry form view
        else:
            # If authentication fails, pass an error message back to the template
            return render(request, 'LOGIN.html', {'error': 'Invalid username or password'})

    # If it's a GET request, just render the blank login page
    return render(request, 'LOGIN.html')


# --- NEW LOGOUT VIEW ---
def logout_view(request):
    logout(request)  # This destroys the session cookie in the browser
    return redirect('landing_page')  # Send them back to the login page after logging out

'''
@login_required(login_url='login_view')
def upload_file(request):
    if request.method == "POST":
        file = request.FILES.get("myfile")

        if not file.name.endswith('.pdf'):
            messages.error(request, "Only PDF files allowed")
            return redirect('contact_form')

        Document.objects.create(file=file)
        messages.success(request, "Uploaded successfully")

        return redirect('contact_form')
'''
#---------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------
#function to see the form data as a table

@login_required(login_url='login_view')
def form_data(request):
    users = list(UserData.objects.prefetch_related('applications').all())

    for user in users:
        apps = sorted(user.applications.all(), key=lambda a: a.applied_at or a.id, reverse=True)
        user.current_status = apps[0].status if apps else "N/A"

    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'form_data.html', {
        'users': page_obj.object_list,
        'page_obj': page_obj,
        'active_page': 'form_data',
    })
#---------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------

def form_submit(request):
    if request.method == "POST":
        user_data = UserData.objects.create(
            user=request.user,
            name=request.POST['name'],
            email=request.POST['email'],
            gender=request.POST['gender'],
            country=request.POST['country'],
            message=request.POST['message'],
            skills=",".join(request.POST.getlist('skills'))
        )

        file = request.FILES.get('myfile')

        if file:
            Document.objects.create(
                user_data=user_data,
                file=file
            )

        return redirect("success_page")
        

#-------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------
#function to get data from the file in AJAX way

def ajax_data(request):

    if request.method == "POST":

        name = request.POST.get("name")
        email = request.POST.get("email")
        gender = request.POST.get("gender")
        country = request.POST.get("country")
        message = request.POST.get("message")

        skills = request.POST.getlist("skills")

        myfile = request.FILES.get("myfile")

        
        user_data = UserData.objects.create(

            name=name,
            email=email,
            gender=gender,
            country=country,
            message=message,
            skills=",".join(skills)

        )

        
        Document.objects.create(

            user_data=user_data,
            file=myfile

        )
        '''
        return JsonResponse({

            "message": "Data Saved Successfully"

        })
        '''
        messages.success(request, "Data saved successfully")
        return redirect('form_success')
    return render(request, "ajaxForm.html", {
        'active_page': 'ajax'
    })

#-------------------------------------------------------------------------------------------------------
# edit form function

def edit_data(request, id):
    data = UserData.objects.get(id=id)

    return render(
        request,
        "apply_job.html",
        {"data": data}
    )

#------------------------------------------------------------------------------------------------------
# delete record function

def delete_data(request, id):

    data = UserData.objects.get(id=id)

    data.delete()

    messages.success(
        request,
        "Record deleted successfully"
    )

    return redirect("form_data")

#---------------------------------------------------------------------------------------------------------
@login_required(login_url='login_view')
def search_candidates(request):
    skill = request.GET.get("skill", "").strip()
    experience = request.GET.get("experience", "").strip()
    search_type = request.GET.get("search_type", "or")

    min_exp = int(experience) if (experience and experience.isdigit()) else None
    search_data = search_candidates_service(
        skill_query=skill,
        min_experience=min_exp,
        search_type=search_type
    )

    context = {
        'active_page': 'search_candidates',
        'skill': skill,
        'experience': experience,
        'results': search_data.get("raw_queryset", UserSkill.objects.none()),
        'candidate_results': search_data["candidate_results"],
    }
    return render(request, 'search_candidates.html', context)


#---------------------------------------------------------------------------------------------------------
# candidate PROFILE
@login_required(login_url='login_view')
def candidate_profile(request, id):
    candidate = get_object_or_404(UserData, id=id)
    skills = UserSkill.objects.filter(user_data=candidate).order_by('-years_of_experience')
    document = Document.objects.filter(user_data=candidate).first()

    context = {
        'candidate': candidate,
        'skills': skills,
        'document': document,
    }
    return render(request, 'candidate_profile.html', context)

#---------------------------------------------------------------------------------------------------------
#function for ATS dashboard
@login_required(login_url='login_view')
def ats_dashboard(request):
    metrics = get_dashboard_metrics()
    skills_data = get_skills_distribution(limit=15)
    experience_data = get_experience_distribution(limit=15)
    charts = build_plotly_charts(skills_data, experience_data)

    top_skills_raw = (
        UserSkill.objects
        .values('skill__name')
        .annotate(total=Count('skill'))
        .order_by('-total')
    )

    context = {
        'active_page': 'ats_dashboard',
        'total_candidates': metrics['total_candidates'],
        'total_skills': metrics['total_skills'],
        'total_user_skills': metrics['total_user_skills'],
        'top_skills': top_skills_raw,
        'chart': charts['skills_chart'],
        'avg_exp_chart': charts['experience_chart'],
    }
    return render(request, 'ATS_dashboard.html', context)


#function for logs page
def logs(request):

    logs = ActivityLog.objects.select_related(
        "candidate",
        "performed_by"
    ).order_by(
        "-created_at"
    )
    return render(
        request,
        'logs.html',
        {
            'logs': logs,
            'active_page' : 'logs',
        }
    )