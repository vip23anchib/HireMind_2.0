from django.urls import path
from . import views


urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('members/', views.members, name='members'),
    path('members/<int:id>/', views.details, name='details'),
    path('testing/', views.testing, name='testing'), 
    path('members/add/', views.add_member, name='add_member'),
    
]

