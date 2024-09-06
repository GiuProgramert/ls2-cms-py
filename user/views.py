from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.generic import ListView
from .models import CustomUser, Role
from .forms import CustomUserCreationForm
from django.contrib.auth.mixins import UserPassesTestMixin
from roles.utils import PermissionEnum


def login_view(request):
    """
    Maneja la vista de inicio de sesión.

    Si el método de la solicitud es POST, intenta autenticar al usuario con el nombre de usuario y la contraseña proporcionados.
    Si la autenticación es exitosa, redirige al usuario a la página de inicio. En caso contrario, muestra un mensaje de error.

    Args:
        request (HttpRequest): La solicitud HTTP recibida.

    Returns:
        HttpResponse: Redirige al usuario a la página de inicio en caso de éxito,
        o renderiza la página de inicio de sesión con un mensaje de error.
    """

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
    """
    Maneja la vista de cierre de sesión.

    Cierra la sesión del usuario actual y lo redirige a la página de inicio de sesión.

    Args:
        request (HttpRequest): La solicitud HTTP recibida.

    Returns:
        HttpResponse: Redirige al usuario a la página de inicio de sesión.
    """

    logout(request)
    return redirect("login")


class UserListView(UserPassesTestMixin, ListView):
    """
    Vista para listar usuarios que no son administradores.

    Muestra una lista de usuarios, excluyendo aquellos que tienen el rol de 'Administrador'.

    Attributes:
        model (Model): El modelo `CustomUser` que se va a listar.
        template_name (str): La plantilla que se renderiza para esta vista.
        context_object_name (str): El nombre de la variable de contexto que contendrá la lista de usuarios en la plantilla.

    Methods:
        get_queryset(): Filtra los usuarios para excluir aquellos con el rol de 'Administrador'.
    """

    model = CustomUser
    template_name = "user/user_list.html"
    context_object_name = "users"

    def get_queryset(self):
        """
        Filtra los usuarios excluyendo aquellos que tienen el rol de 'Administrador'.

        Returns:
            QuerySet: El conjunto de usuarios filtrado.
        """
        administradores = Role.objects.filter(name="Administrador")
        return CustomUser.objects.exclude(roles__in=administradores)

    def test_func(self):
        """
        Solo permite acceso a usuarios con permisos específicos.
        """
        return self.request.user.tiene_permisos([PermissionEnum.MANEJO_ROLES])

    def handle_no_permission(self):
        """
        Redirige a la página de "forbidden" si no se tiene permiso.
        """
        return redirect("forbidden")


def register(request):
    """
    Maneja el registro de nuevos usuarios.

    Si la solicitud es un POST, procesa el formulario enviado para registrar un nuevo usuario.
    Si el formulario es válido, guarda el nuevo usuario en la base de datos, inicia sesión con ese usuario
    y redirige a la página de inicio ('home'). Si el formulario no es válido, o si la solicitud es un GET,
    presenta el formulario de registro vacío.

    Args:
        request (HttpRequest): La solicitud HTTP que se está procesando.

    Returns:
        HttpResponse: Renderiza la plantilla 'user/register.html' con el formulario de registro.
                      Si el registro es exitoso, redirige a la página 'home'.
    """

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(
                "home"
            )  # redirige a home una vez se completo correctamente el form
    else:
        form = CustomUserCreationForm()
    return render(request, "user/register.html", {"form": form})
