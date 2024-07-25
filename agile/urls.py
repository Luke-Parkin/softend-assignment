from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("dashboard/", include("tickets.urls")),
    path("", include("authentication.urls")),
]
