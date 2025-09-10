from django.contrib import admin
from django.urls import path, include
from .views import health_check

urlpatterns = [
    path('', health_check),
    path('admin/', admin.site.urls),
    path("api/v1/accounts/", include(("users.urls", "users"), namespace="accounts")),  
]
