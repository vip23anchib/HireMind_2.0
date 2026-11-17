"""
Main Project URL Configuration.
Exposes both modern REST API v1 endpoints (with OpenAPI/Swagger docs)
and preserves legacy Django template views for seamless backward compatibility.
"""

from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from members.views import landing_page

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),

    # OpenAPI 3.0 Documentation & Swagger UI
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # REST API v1 Endpoints
    path('api/v1/', include('api.v1.urls')),

    # Legacy Web Views (Preserved for backwards compatibility)
    path('', landing_page, name='landing_page'),
    path('dashboard/', include('members.urls')),
    path('', include('applicants.urls')),
    path('', include('jobs.urls')),
    path('', include('relationships.urls')),
    path('landing-dashboard/', include('members.urls')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
