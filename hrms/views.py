from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.utils import timezone
from core.utils import api_response

class HealthCheckAPIView(APIView):
    """
    Health check endpoint for monitoring service status.
    """
    permission_classes = [AllowAny]
    
    def get(self, request, *args, **kwargs):
        response = {
                "service": "HRMS API",
                "uptime": timezone.now().isoformat(),
                "endpoint": "health-check"
        }
        return api_response(
            message="Service is running",
            data=response,
            status_code=status.HTTP_201_CREATED
        )