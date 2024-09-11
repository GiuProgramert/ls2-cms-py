from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.generic import ListView
from .models import CustomUser, Role
from .forms import CustomUserCreationForm
from django.contrib.auth.mixins import UserPassesTestMixin
from roles.utils import PermissionEnum
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm
from django.contrib.auth import update_session_auth_hash
from .forms import CustomPasswordChangeForm


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
    return redirect("/")


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
        Verifica si el usuario actual tiene permiso para acceder a esta vista.

        Returns:
            bool: True si el usuario tiene permisos, False en caso contrario.
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

    Si la solicitud es POST y el formulario es válido, crea un nuevo usuario y lo autentica.
    Luego, redirige al usuario a la página de inicio, al usuario recien registrado se le asiga el rol de visitante por defecto.
    """
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Fetch the "Visitante" role and assign it to the new user
            visitante_role = Role.objects.get(
                name="Visitante"
            )  # Assumes the role name is "Visitante"
            user.roles.add(visitante_role)  # Assign the role to the user
            user.save()  # Save the user with the new role

            # Log the user in after registration
            login(request, user)
            return redirect("home")  # Redirect to home after successful registration
    else:
        form = CustomUserCreationForm()
    return render(request, "user/register.html", {"form": form})


@login_required
def edit_profile(request):
    """
    Maneja la edición del perfil y cambio de contraseña del usuario.

    Permite al usuario editar su perfil y/o cambiar su contraseña desde la misma vista.
    Muestra mensajes de éxito o error según la validación de los formularios.

    Args:
        request (HttpRequest): La solicitud HTTP recibida.

    Returns:
        HttpResponse: Redirige al usuario a la misma página con los formularios
        de perfil y contraseña, mostrando los mensajes correspondientes.
    """
    if request.method == "POST":
        if "profile_submit" in request.POST:  # Profile form was submitted
            profile_form = ProfileForm(request.POST, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(
                    request, "Perfil actualizado correctamente."
                )  # Success message for profile
            else:
                messages.error(request, "Por favor corrija los errores en el perfil.")

        elif "password_submit" in request.POST:  # Password form was submitted
            password_form = CustomPasswordChangeForm(
                user=request.user, data=request.POST
            )
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(
                    request, password_form.user
                )  # Mantiene la sesión después de cambiar la contraseña
                messages.success(
                    request, "Contraseña actualizada correctamente."
                )  # Mensaje de éxito para contraseña
            else:
                messages.error(
                    request,
                    "Por favor corrija los errores en el formulario de contraseña.",
                )

        return redirect("edit_profile")

    else:
        profile_form = ProfileForm(instance=request.user)
        password_form = CustomPasswordChangeForm(user=request.user)

    return render(
        request,
        "user/edit_profile.html",
        {"profile_form": profile_form, "password_form": password_form},
    )
