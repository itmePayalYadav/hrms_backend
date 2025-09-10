from django.contrib import admin
from django.urls import path, include
from rest_framework.decorators import api_view

@api_view(['GET'])
def health_check(request):
    return Response({"status": "ok", "message": "Service is running"})

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/v1/accounts/", include("users.urls", namespace="accounts"))
]
