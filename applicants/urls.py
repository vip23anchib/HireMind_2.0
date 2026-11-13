from django.urls import path
from . import views
from django.conf import settings

urlpatterns = [
    path('login/', views.login_view, name='login_view'),
    path('registration/', views.form, name='contact_form'),
    path('success/', views.success_view, name='form_success'),
    path('logout/', views.logout_view, name='logout_view'),
    
    path('form-data/', views.form_data, name='form_data'),
    path('ajax-data/', views.ajax_data, name='ajax_data'),
    path('form-data/edit/<int:id>/',views.edit_data,name='edit_data'),
    path("form-data/delete/<int:id>/",views.delete_data,name="delete_data"),

    path('search-candidates/',views.search_candidates,name='search_candidates'),

    path('candidate/<int:id>/',views.candidate_profile,name='candidate_profile'),

    path('ats_dashboard/',views.ats_dashboard,name='ats_dashboard'),

    path('applications/',views.applications_list,name='applications_list'),

    path('applications/<int:application_id>/status/',views.update_application_status,name='update_application_status'),

    path('home-page/',views.home_page,name='home-page'),

    path('logs-page/',views.logs,name='logs'),



]


