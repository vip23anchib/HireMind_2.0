from django.urls import path
from . import views

urlpatterns = [

    path(
        'careers/',
        views.careers,
        name='careers',
    ),

    
    path(
        'jobs/<slug:slug>/',
        views.job_detail,
        name='job_detail'
    ),
   
    path(
        'careers/<slug:slug>/apply/',
        views.apply_job,
        name='apply_job'
    ),




]
