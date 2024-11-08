from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.generic import ListView
from .models import CustomUser, Role
from .forms import (
    CustomPasswordChangeForm,
    CustomUserCreationForm,
    ProfileForm,
    UserSearchForm,
)
from django.contrib.auth.mixins import UserPassesTestMixin
from roles.utils import PermissionEnum
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash


def login_view(request):
    """
    Maneja la vista de inicio de sesión.
    Si la solicitud es un POST, procesa el formulario enviado para iniciar sesión.

    Args:
        request (HttpRequest): La solicitud HTTP que se está procesando.

    Returns:
        HttpResponse: Renderiza la plantilla 'user/login.html' con el formulario de inicio de sesión.
                        Si el inicio de sesión es exitoso, redirige a la página 'home'.
    """

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:  # Ensure the user is active before logging in
                login(request, user)
                return redirect("home")
            else:
                messages.error(
                    request, "Tu cuenta está desactivada. Contacta al administrador."
                )
        else:
            messages.error(request, "Nombre de usuario o contraseña incorrecta.")

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
    Vista para listar usuarios que no son administradores, con funcionalidad de búsqueda y filtrado.

    Muestra una lista de usuarios, excluyendo aquellos que tienen el rol de 'Administrador'.

    Attributes:
        model (Model): El modelo `CustomUser` que se va a listar.
        template_name (str): La plantilla que se renderiza para esta vista.
        context_object_name (str): El nombre de la variable de contexto que contendrá la lista de usuarios en la plantilla.
    """

    model = CustomUser
    template_name = "user/user_list.html"
    context_object_name = "users"

    def get_queryset(self):
        """
        Filtra los usuarios excluyendo aquellos que tienen el rol de 'Administrador' y aplica filtros
        de búsqueda y ordenamiento según el formulario.

        Returns:
            QuerySet: El conjunto de usuarios filtrado.
        """
        queryset = super().get_queryset()
        form = UserSearchForm(self.request.GET or None)

        administradores = Role.objects.filter(name="Administrador")
        queryset = queryset.exclude(roles__in=administradores)

        if form.is_valid():
            search_term = form.cleaned_data.get("search_term", "")
            order_by = form.cleaned_data.get("order_by", "username")
            filter_role = form.cleaned_data.get("filter_role", "all")

            # Filtrar por nombre de usuario o email que contenga el término de búsqueda
            if search_term:
                queryset = queryset.filter(
                    username__icontains=search_term
                ) | queryset.filter(email__icontains=search_term)

            # Filtrar por rol si no es 'all'
            if filter_role != "all":
                queryset = queryset.filter(roles__name=filter_role)

            # Ordenar los resultados
            queryset = queryset.order_by(order_by)

        return queryset

    def get_context_data(self, **kwargs):
        """
        Añade el formulario de búsqueda al contexto.

        Args:
            **kwargs: Argumentos adicionales del contexto.

        Returns:
            dict: El contexto actualizado con el formulario.
        """
        context = super().get_context_data(**kwargs)
        form = UserSearchForm(self.request.GET or None)
        context["form"] = form
        return context

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

            # Fetch the "Visitante" role and assign it to the new user
            suscriptor_role = Role.objects.get(
                name="Suscriptor"
            )  # Assumes the role name is "Visitante"
            user.roles.add(suscriptor_role)  # Assign the role to the user
            user.save()  # Save the user with the new role

            # Log the user in after registration
            login(request, user)
            return redirect("home")
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


@login_required
def toggle_user_status(request, user_id):
    """
    Toggle the active/inactive status of a user.
    """
    user = get_object_or_404(CustomUser, pk=user_id)

    if user.is_active:
        user.is_active = False
        messages.success(request, f"{user.username} ha sido desactivado.")
    else:
        user.is_active = True
        messages.success(request, f"{user.username} ha sido activado.")

    user.save()
    return redirect(
        "user-list"
    )  # Change 'user_list' to the actual URL name for your user list view
