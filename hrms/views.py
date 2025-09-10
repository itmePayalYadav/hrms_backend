from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.utils import timezone

@api_view(['GET'])
@permission_classes([AllowAny]) 
def health_check(request):
    """
    Health check endpoint for monitoring service status.
    """
    response_data = {
        "status": "success",
        "message": "Service is running",
        "data": {
            "service": "HRMS API",
            "uptime": timezone.now().isoformat()
        }
    }
    return Response(response_data, status=status.HTTP_200_OK)
