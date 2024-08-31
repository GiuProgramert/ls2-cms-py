from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.generic import ListView
from .models import CustomUser, Role

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
            messages.error(request, "Nombre de usuario o contraseña incorrecta")

    return render(request, "user/login.html")


def logout_view(request):
    logout(request)
    return redirect("login")

class UserListView(ListView):
    model = CustomUser
    template_name = 'user/user_list.html'  # La plantilla que vamos a crear
    context_object_name = 'users'  # El nombre del contexto en la plantilla
    
    def get_queryset(self):
        # Filtrar usuarios que no sean administradores
        administradores = Role.objects.filter(name='Administrador')
        return CustomUser.objects.exclude(roles__in=administradores)