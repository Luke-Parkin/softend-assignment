from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


# This formats the display for the admin page
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ["username", "email", "is_superuser"]


admin.site.register(CustomUser, CustomUserAdmin)
