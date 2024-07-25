from django.urls import path
from . import views

urlpatterns = [
    path("", views.landing, name="landing"),
    path("auth/register", views.register, name="register"),
    path("auth/login", views.login_page, name="login"),
    path("auth/logout", views.logout_page, name="logout"),
]
