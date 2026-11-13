
from django.contrib import admin
from django.urls import include, path
import sys
from django.conf import settings
from django.conf.urls.static import static

print("--- PROJECT URLS are LOADING ---") 

from members.views import landing_page

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', landing_page, name='landing_page'),

    path('dashboard/', include('members.urls')), #dashboard

    path('',include('applicants.urls')) ,#registration
    
    path('', include('jobs.urls')),

    path('', include('relationships.urls')),
    
    path('landing-dashboard/', include('members.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)