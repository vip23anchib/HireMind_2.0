from django.shortcuts import (
    render,
    get_object_or_404
)
from .models import Job


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




