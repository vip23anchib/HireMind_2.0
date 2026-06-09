
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, redirect

from django.contrib.auth.decorators import login_required

from applicants.models import ActivityLog
from django.contrib.auth.models import User

from django.shortcuts import render
from .models import Author

import time

from applicants.models import UserData

'''
@login_required(login_url='login_view')
def search_authors(request):

    query = request.GET.get('author', '')

    authors = Author.objects.none()

    search_time = None

    if query:

        start_time = time.perf_counter()

        authors = Author.objects.filter(
            name__icontains=query
        )

        end_time = time.perf_counter()

        search_time = round(
            end_time - start_time,
            6
        )

    context = {
        'authors': authors,
        'query': query,
        'search_time': search_time,
        'active_page': 'indexing',
    }


    return render(
        request,
        'search_authors.html',
        context
    )
'''



def search_candidates_index(request):

    query = request.GET.get('name', '')

    candidates = UserData.objects.none()

    search_time = None

    if query:

        start_time = time.perf_counter()

        candidates = UserData.objects.filter(
            name__icontains=query
        )

        end_time = time.perf_counter()

        search_time = round(
            end_time - start_time,
            6
        )

    context = {
        'candidates': candidates,
        'query': query,
        'search_time': search_time,
    }

    return render(
        request,
        'search_authors.html',
        context
    )