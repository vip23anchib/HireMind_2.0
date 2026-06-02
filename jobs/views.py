from django.shortcuts import (
    render,
    get_object_or_404
)
from .models import Job
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages




@login_required(login_url='login_view')
def careers(request):

    jobs = Job.objects.filter(
        is_active=True
    ).order_by('-created_at')

    context = {
        'jobs': jobs,
        'active_page': 'careers_list',
    }

    return render(
        request,
        'careers.html',
        context
    )

#function tfor showing job details on career page
@login_required(login_url='login_view')
def job_detail(request, slug):

    job = get_object_or_404(
        Job,
        slug=slug,
        is_active=True
    )

    context = {
        'job': job
    }

    return render(
        request,
        'job_detail.html',
        context
    )


@login_required(login_url='login_view')
def apply_job(request, slug):

    job = get_object_or_404(
        Job,
        slug=slug,
        is_active=True
    )

    context = {
        'job': job
    }

    return render(
        request,
        'apply_job.html',
        context
    )


#to manage , add , create and delete jobs 
@login_required(login_url='login_view')
def manage_jobs(request):

    jobs = Job.objects.all().order_by(
        '-created_at'
    )


    return render(
        request,
        'manage_jobs.html',
        {
            'jobs': jobs,
            'active_page': 'manage_jobs'
        }
    )


#function to make job active or inactive 
@login_required(login_url='login_view')
def toggle_job_status(request, id):

    job = get_object_or_404(
        Job,
        id=id
    )

    job.is_active = not job.is_active

    job.save()

    return redirect(
        'manage_jobs'
    )


#function to let HR create jobs 
@login_required(login_url='login_view')
def create_job(request):

    if request.method == "POST":

        Job.objects.create(

            title=request.POST['title'],

            slug=request.POST['slug'],

            department=request.POST['department'],

            location=request.POST['location'],

            job_type=request.POST['job_type'],

            description=request.POST['description'],

            requirements=request.POST['requirements'],

            responsibilities=request.POST['responsibilities'],

            experience_required=request.POST['experience_required'],

            is_active=True

        )

        messages.success(
            request,
            "Job created successfully"
        )

        return redirect(
            'manage_jobs'
        )

    return render(
        request,
        'create_job.html',
        {
            'active_page': 'manage_jobs'
        }
    )

    
#function to edit job 
@login_required(login_url='login_view')
def edit_job(request, id):

    job = get_object_or_404(
        Job,
        id=id
    )

    if request.method == "POST":

        job.title = request.POST['title']
        job.slug = request.POST['slug']
        job.department = request.POST['department']
        job.location = request.POST['location']
        job.job_type = request.POST['job_type']
        job.description = request.POST['description']
        job.requirements = request.POST['requirements']
        job.responsibilities = request.POST['responsibilities']
        job.experience_required = request.POST['experience_required']

        job.save()

        return redirect(
            'manage_jobs'
        )

    return render(
        request,
        'edit_job.html',
        {
            'job': job,
            'active_page': 'manage_jobs'
        }
    )

#function to show about us page
@login_required(login_url='login_view')
def about_us(request):

    

    return render(
        request,
        'aboutUs.html',
        {
            'active_page': 'about_us',
        }
    )

#function to show services page
@login_required(login_url='login_view')
def services(request):

    

    return render(
        request,
        'services.html',
        {
            'active_page': 'services',
        }
    )

#function to show services page
@login_required(login_url='login_view')
def contact(request):

    

    return render(
        request,
        'contact.html',
        {
            'active_page': 'contact',
        }
    )