"""
Health Check API Views.
Provides real-time liveness and readiness probes for Docker, Kubernetes, and uptime monitoring.
"""

from rest_framework import views, permissions, status
from rest_framework.response import Response
from django.db import connection
from drf_spectacular.utils import extend_schema, OpenApiResponse
import redis
from django.conf import settings


class HealthCheckAPIView(views.APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        responses={
            200: OpenApiResponse(description="All system services operational"),
            503: OpenApiResponse(description="One or more critical services degraded"),
        },
        description="Liveness and readiness health probe verifying database and cache connectivity."
    )
    def get(self, request):
        health_status = {
            "status": "healthy",
            "version": "1.0.0",
            "checks": {
                "database": "unknown",
                "redis": "unknown",
            }
        }

        # 1. Database Check
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            health_status["checks"]["database"] = "healthy"
        except Exception as e:
            health_status["status"] = "degraded"
            health_status["checks"]["database"] = f"unhealthy: {str(e)}"

        # 2. Redis Cache & Broker Check
        try:
            broker_url = getattr(settings, 'CELERY_BROKER_URL', 'redis://localhost:6379/0')
            r = redis.Redis.from_url(broker_url, socket_timeout=2)
            r.ping()
            health_status["checks"]["redis"] = "healthy"
        except Exception as e:
            # Redis degradation is non-fatal if eager mode is permitted in dev
            health_status["checks"]["redis"] = f"unreachable ({str(e)})"
            if not getattr(settings, 'CELERY_TASK_ALWAYS_EAGER', False):
                health_status["status"] = "degraded"

        status_code = status.HTTP_200_OK if health_status["status"] == "healthy" else status.HTTP_503_SERVICE_UNAVAILABLE
        return Response(health_status, status=status_code)
