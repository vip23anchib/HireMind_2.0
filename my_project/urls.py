
from django.contrib import admin
from django.urls import include, path
import sys
from django.conf import settings
from django.conf.urls.static import static

print("--- PROJECT URLS are LOADING ---") 

urlpatterns = [
    path('admin/', admin.site.urls),

    path('dashboard/', include('members.urls')), #dashboard

    path('',include('myForm.urls')) ,#registration
    
    path('', include('jobs.urls')),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)