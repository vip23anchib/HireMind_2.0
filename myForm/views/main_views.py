
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required # Import protection decorator

from ..models import UserData, Document

from django.contrib import messages

from django.http import JsonResponse

from pypdf import PdfReader

from django.core.paginator import Paginator

from ..models import UserSkill, Skill

from django.db.models import Q

from django.db.models import Count , Avg
import plotly.express as px
from plotly.offline import plot

from jobs.models import Job
from myForm.models import UserData, Application

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

    total_applications = Application.objects.count()

    active_jobs = Job.objects.filter(
        is_active=True
    ).count()

    total_candidates = UserData.objects.count()

    shortlisted = Application.objects.filter(
        status='Shortlisted'
    ).count()

    interviews = Application.objects.filter(
        status='Interview Scheduled'
    ).count()

    hired = Application.objects.filter(
        status='Hired'
    ).count()

    recent_applications = Application.objects.select_related(
        'candidate',
        'job'
    ).order_by(
        '-applied_at'
    )[:5]

    context = {

        'total_applications': total_applications,
        'active_jobs': active_jobs,
        'total_candidates': total_candidates,
        'shortlisted': shortlisted,
        'interviews': interviews,
        'hired': hired,
        'recent_applications': recent_applications,

    }

    return render(
        request,
        "hr_homePage.html",
        context
    )



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
    
    users = UserData.objects.all()

    #paginators
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)


    #new code for reading pdf and showing in table 
    '''
    for user in users:
        user.pdf_content = "No PDF"

        doc = user.document_set.first()

        if doc:

            try:
                reader = PdfReader(doc.file.path)

                text = ""

                for page in reader.pages:
                    page_text = page.extract_text()

                    if page_text:
                        text += page_text

                user.pdf_content = text[:200]

            except Exception:
                user.pdf_content = "Could not read PDF"
    '''
    return render(request, 'form_data.html', {
        'users': users,
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
        "FORM.html",
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
# candidate search 
@login_required(login_url='login_view')
def search_candidates(request):

    # Get form values
    skill = request.GET.get("skill", "").strip()
    experience = request.GET.get("experience", "").strip()

    #search type AND or OR
    search_type = request.GET.get(
    "search_type",
    "or")

    # Default empty results
    results = UserSkill.objects.none()
    candidate_results = []

    # Run search only when skill is entered
    if skill:

        # Convert:
        # "Python,Django,React" into : ["Python", "Django", "React"]
        skills_list = [
            s.strip()
            for s in skill.split(',')
            if s.strip()
        ]

        # Build OR query
        if search_type == "or":
            query = Q()
            for skill_name in skills_list:
                query |= Q(
                skill__name__icontains=skill_name
            )

            results = UserSkill.objects.filter(query)
        
        else:
            candidate_ids = None
            for skill_name in skills_list:
                # Get a unique set of user IDs who have the current skill in the loop
                skill_candidates = set(
                    UserSkill.objects.filter(
                        skill__name__icontains=skill_name
                    ).values_list(
                        'user_data_id',
                        flat=True
                    )

                )
                # If this is the first skill we are checking, kickstart our master list
                if candidate_ids is None:
                    candidate_ids = skill_candidates

                # intersection (&) operator. keeps ONLY the user IDs that exist in both the master list AND the new skill list.
                # This guarantees that the final candidate_ids list only contains users who have ALL the skills.
                else:
                    candidate_ids = (
                        candidate_ids
                        &
                        skill_candidates
                )
            # STEP 2: Fetch all the UserSkill database records for these qualified users
            # This acts like a SQL: WHERE user_data_id IN (list_of_ids)
            results = UserSkill.objects.filter(
                user_data_id__in=candidate_ids #WHERE user_data_id IN (39,40)
            )

            # STEP 3: Prune the results to ONLY show rows matching the searched skills (OR logic)
            # Why? A user might have 20 skills. We only want to see the rows for the skills we searched for.
            query = Q()
            for skill_name in skills_list:
                # Chain each skill search using the OR operator (|=)
                # It creates a query like: WHERE skill LIKE '%A%' OR skill LIKE '%B%'
                query |= Q(
                    skill__name__icontains=skill_name
                )
            results = results.filter(query)
            

        # Apply experience filter
        if experience:

            results = results.filter(
                years_of_experience__gte=experience
            )

        # Highest experience first
        results = results.order_by(
            '-years_of_experience'
        )

        candidate_map = {} #to show only non-duplicates rows so making dictionary of candidate, skills and experience 
        for item in results:
            candidate_id = item.user_data.id
            if candidate_id not in candidate_map:
                candidate_map[candidate_id] = {
                    'candidate': item.user_data,
                    'skills': [
                        item.skill.name
                    ],
                    'experience':
                    item.years_of_experience
                    or 0
                }
            else:

                candidate_map[candidate_id][
                    'skills'
                ].append(
                    item.skill.name
                )
                # Update highest experience
                candidate_map[candidate_id][
                    'experience'
                ] = max(
                    candidate_map[candidate_id][
                        'experience'
                    ],
                    item.years_of_experience
                    or 0
                )
        for data in candidate_map.values():
            matched_count = len(
                data['skills']
            )
            requested_count = len(
                skills_list
            )   

            score = round((matched_count / requested_count) * 100)

            data['score'] = score
       
        #function to find missing skill
        for data in candidate_map.values():
            candidate_skills = set(
                data['skills']
            )
            requested_skills = set(
                skills_list
            )
            missing_skills = (
                requested_skills
                -           
                candidate_skills
                )

            data['missing_skills'] = list(
                missing_skills
            )
            print(candidate_results)
        
        candidate_results = list(
        candidate_map.values()
)
    #function to sort result in descending order of ATS score
    candidate_results.sort(
        key=lambda x: (
        x['score'],
        x['experience']
    ),
        reverse=True
    )
    
    print(candidate_results)
    context = {
        'active_page': 'search_candidates',
        'skill': skill,
        'experience': experience,
        'results': results,
        'candidate_results': candidate_results,
    }

    return render(
        request,
        'search_candidates.html',
        context
    )

#---------------------------------------------------------------------------------------------------------
# candidate PROFILE
@login_required(login_url='login_view')
def candidate_profile(request, id):

    candidate = UserData.objects.get(id=id)

    skills = UserSkill.objects.filter(
        user_data=candidate
    ).order_by('-years_of_experience')

    print("Candidate ID =", candidate.id)

    document = Document.objects.filter(
        user_data=candidate
    ).first()

    context = {
        'candidate': candidate,
        'skills': skills,
        'document': document,
    }

    return render(
        request,
        'candidate_profile.html',
        context
    )


#---------------------------------------------------------------------------------------------------------
#function for ATS dashboard
@login_required(login_url='login_view')
def ats_dashboard(request):

    total_candidates = UserData.objects.count()

    total_skills = Skill.objects.count()

    total_user_skills = UserSkill.objects.count()

    top_skills = (
        UserSkill.objects
        .values('skill__name')
        .annotate(
            total=Count('skill')
        )
        .order_by('-total')
    )
    print(list(top_skills))

    avg_experience = (
        UserSkill.objects
        .values('skill__name')
        .annotate(
            avg_years=Avg(
                'years_of_experience'
            )
        )
        .order_by(
            '-avg_years'
        )
    )

    #for top skills bar chart
    skills = []
    counts = []
    for skill in top_skills:
        skills.append(
            skill['skill__name']
        )
        counts.append(
            skill['total']
        )
        
    #plotly chart
    fig = px.bar(
        x=skills,
        y=counts,
        title="Top Skills"
    )   
    #convert chart to html
    chart = plot(
        fig,
        output_type='div'
    )


    #for avg experience bar chart
    avg_skill_names = []
    avg_skill_years = []
    for item in avg_experience:
        avg_skill_names.append(
            item['skill__name']
        )
        avg_skill_years.append(
            round(
                item['avg_years'],
                2
            )
        )
    avg_exp_chart = px.bar(
        x=avg_skill_names,
        y=avg_skill_years,
        title="Average Experience By Skill"
    ) 
    avg_exp_chart = plot(#convertbto html
        avg_exp_chart,
        output_type='div'
    )

    context = {
         'active_page': 'ats_dashboard',

        'total_candidates': total_candidates,

        'total_skills': total_skills,

        'total_user_skills': total_user_skills,

        'top_skills': top_skills,

        'chart': chart,

        'avg_exp_chart': avg_exp_chart,
    }
    
    print(type(avg_exp_chart))
    print(len(avg_exp_chart))
    return render(
        request,
        'ATS_dashboard.html',
        context
    )