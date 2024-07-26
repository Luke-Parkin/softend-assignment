from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django import forms


def landing(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    else:
        return render(request, "landing.html")


User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse("login") + "?signedup=true")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomUserCreationForm()

    return render(request, "register.html", {"form": form})


def login_page(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("dashboard")
        else:
            return redirect(reverse("login") + "?failed=true")

    form = AuthenticationForm()
    signedup = request.GET.get("signedup", None)
    failed = request.GET.get("failed", None)
    return render(
        request, "login.html", {"form": form, "signedup": signedup, "failed": failed}
    )


def logout_page(request):
    logout(request)
    return redirect("landing")
