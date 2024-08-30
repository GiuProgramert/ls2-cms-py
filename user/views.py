from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(
                "home"
            )  # Cambia 'home' por la URL a la que quieras redirigir después del login
        else:
            messages.error(request, "Username or password incorrect")

    return render(request, "user/login.html")


def logout_view(request):
    logout(request)
    return redirect("login")
