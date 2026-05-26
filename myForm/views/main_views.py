
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

from ..models import UserSkill

from django.db.models import Q
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
            return redirect('main')  # Redirects to your data entry form view
        else:
            # If authentication fails, pass an error message back to the template
            return render(request, 'LOGIN.html', {'error': 'Invalid username or password'})

    # If it's a GET request, just render the blank login page
    return render(request, 'LOGIN.html')


# --- NEW LOGOUT VIEW ---
def logout_view(request):
    logout(request)  # This destroys the session cookie in the browser
    return redirect('login_view')  # Send them back to the login page after logging out

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
    paginator = Paginator(users, 5)
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
        'page_obj': page_obj
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

    # Default empty results
    results = UserSkill.objects.none()

    # Run search only when skill is entered
    if skill:

        # Convert:
        # "Python,Django,React"
        # into:
        # ["Python", "Django", "React"]

        skills_list = [
            s.strip()
            for s in skill.split(',')
            if s.strip()
        ]

        # Build OR query
        query = Q()

        for skill_name in skills_list:

            query |= Q(
                skill__name__icontains=skill_name
            )

        # Apply skill filter
        results = UserSkill.objects.filter(query)

        # Apply experience filter
        if experience:

            results = results.filter(
                years_of_experience__gte=experience
            )

        # Highest experience first
        results = results.order_by(
            '-years_of_experience'
        )

    context = {
        'active_page': 'search_candidates',
        'skill': skill,
        'experience': experience,
        'results': results,
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
        'active_page': 'search_candidates',
        'document': document,
    }

    return render(
        request,
        'candidate_profile.html',
        context
    )