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

    path(
        'manage/',
        views.manage_jobs,
        name='manage_jobs'
    ),

    path(
        'job/<int:id>/toggle/',
        views.toggle_job_status,
        name='toggle_job_status'
    ),

    path(
        'create-job/',
        views.create_job,
        name='create_job'
    ),

    path(
        'edit-job/<int:id>/',
        views.edit_job,
        name='edit_job'
    ),



]
