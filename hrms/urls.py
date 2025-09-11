from django.contrib import admin
from django.urls import path, include
from .views import HealthCheckAPIView

urlpatterns = [
    path('admin/', admin.site.urls),
    path("health/", HealthCheckAPIView.as_view(), name="health-check"),
    path("api/v1/accounts/", include(("users.urls", "users"), namespace="accounts")),  
]
