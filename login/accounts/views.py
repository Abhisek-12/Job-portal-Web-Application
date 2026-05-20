from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import redirect, render


def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("login")

        User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, "Account created successfully.")
        return redirect("login")
    return render(request, "signup.html")


def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")

        messages.error(request, "Invalid credentials")
    return render(request, "login.html")


def user_logout(request):
    logout(request)
    return redirect("login")


@login_required
def home(request):
    return HttpResponse("Welcome! You are logged in.")
