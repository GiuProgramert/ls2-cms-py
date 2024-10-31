from django.urls import reverse_lazy
from django.views.generic import UpdateView
from django.contrib.auth.mixins import UserPassesTestMixin
from user.models import CustomUser
from user.forms import RoleAssignmentForm
from roles.utils import PermissionEnum
from django.shortcuts import render, redirect, get_object_or_404
from roles.forms import RoleForm
from roles.models import Role
from notification.utils import (
    send_email,
)  # Import the send_email function from your utils
from django.template.loader import render_to_string


class RoleAssignmentView(UserPassesTestMixin, UpdateView):
    """
    Vista para asignar roles a un usuario específico.

    Esta vista permite a los usuarios con los permisos adecuados asignar o modificar los roles de un usuario.
    Utiliza una vista basada en clases (`UpdateView`) para manejar la actualización de los roles.

    Attributes:
        model (Model): El modelo `CustomUser` que se va a actualizar.
        form_class (Form): El formulario que se utilizará para la asignación de roles.
        template_name (str): La plantilla que se renderiza para esta vista.
        success_url (str): La URL a la que se redirige después de un formulario exitoso.

    Methods:
        test_func(self): Método que verifica si el usuario tiene permiso para acceder a esta vista.
    """

    model = CustomUser
    form_class = RoleAssignmentForm
    template_name = "roles/assign_roles.html"
    success_url = reverse_lazy("user-list")

    def form_valid(self, form):
        response = super().form_valid(form)  # Save the updated form

        # Fetch the user whose roles were updated
        user = self.object

        # Compose the email content using a template (or hardcode it if needed)
        subject = "Tu rol ha sido cambiado"
        html_content = render_to_string(
            "roles/changed_role_notification.html",
            {
                "user": user,
                "new_roles": user.roles.all(),  # Fetch the new roles assigned to the user
            },
        )

        # Send email notification
        send_email(user.email, subject, html_content)

        return response

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


def role_list(request):
    """
    Vista que muestra la lista de roles.

    Solo los usuarios autenticados y con el permiso `MANEJO_ROLES` pueden
    acceder a esta vista. Si no se cumplen las condiciones, se redirige al
    usuario a la página de login o a la página de acceso prohibido.

    Args:
        request (HttpRequest): La solicitud HTTP.

    Returns:
        HttpResponse: Renderiza la plantilla 'roles/role_list.html' o redirige.
    """

    if not request.user.is_authenticated:
        return redirect("login")

    if not request.user.tiene_permisos([PermissionEnum.MANEJO_ROLES]):
        return redirect("forbidden")

    roles = Role.objects.all()

    return render(request, "roles/role_list.html", {"roles": roles})


def role_detail(request, pk):
    """
    Vista que muestra el detalle de un rol específico.

    Solo los usuarios autenticados y con el permiso `MANEJO_ROLES` pueden
    acceder a esta vista. Si no se cumplen las condiciones, se redirige al
    usuario a la página de login o a la página de acceso prohibido.

    Args:
        request (HttpRequest): La solicitud HTTP.
        pk (int): El ID del rol.

    Returns:
        HttpResponse: Renderiza la plantilla 'roles/role_detail.html' o redirige.
    """

    if not request.user.is_authenticated:
        return redirect("login")

    if not request.user.tiene_permisos([PermissionEnum.MANEJO_ROLES]):
        return redirect("forbidden")

    role = get_object_or_404(Role, pk=pk)
    return render(request, "roles/role_detail.html", {"role": role})


def role_create(request):
    """
    Vista que permite la creación de un nuevo rol.

    Solo los usuarios autenticados y con el permiso `MANEJO_ROLES` pueden
    acceder a esta vista. Si no se cumplen las condiciones, se redirige al
    usuario a la página de login o a la página de acceso prohibido.

    Args:
        request (HttpRequest): La solicitud HTTP.

    Returns:
        HttpResponse: Renderiza la plantilla 'roles/role_form.html' o redirige.
    """

    if not request.user.is_authenticated:
        return redirect("login")

    if not request.user.tiene_permisos([PermissionEnum.MANEJO_ROLES]):
        return redirect("forbidden")

    if request.method == "POST":
        form = RoleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("role-list")
    else:
        form = RoleForm()

    return render(request, "roles/role_form.html", {"form": form})


def role_update(request, pk):
    """
    Vista que permite actualizar un rol existente.

    Solo los usuarios autenticados y con el permiso `MANEJO_ROLES` pueden
    acceder a esta vista. Si no se cumplen las condiciones, se redirige al
    usuario a la página de login o a la página de acceso prohibido.

    Args:
        request (HttpRequest): La solicitud HTTP.
        pk (int): El ID del rol a actualizar.

    Returns:
        HttpResponse: Renderiza la plantilla 'roles/role_form.html' o redirige.
    """

    if not request.user.is_authenticated:
        return redirect("login")

    if not request.user.tiene_permisos([PermissionEnum.MANEJO_ROLES]):
        return redirect("forbidden")

    # Obtener el rol que se va a actualizar
    role = get_object_or_404(Role, pk=pk)

    if request.method == "POST":
        form = RoleForm(request.POST, instance=role)
        if form.is_valid():
            form.save()  # Guarda las actualizaciones
            return redirect("role-list")
    else:
        form = RoleForm(instance=role)

    return render(request, "roles/role_form.html", {"form": form})


def role_delete(request, pk):
    """
    Vista que permite eliminar un rol existente.

    Solo los usuarios autenticados y con el permiso `MANEJO_ROLES` pueden
    acceder a esta vista. Si no se cumplen las condiciones, se redirige al
    usuario a la página de login o a la página de acceso prohibido.

    Args:
        request (HttpRequest): La solicitud HTTP.
        pk (int): El ID del rol a eliminar.

    Returns:
        HttpResponse: Renderiza la plantilla 'roles/role_confirm_delete.html' o redirige.
    """

    if not request.user.is_authenticated:
        return redirect("login")

    if not request.user.tiene_permisos([PermissionEnum.MANEJO_ROLES]):
        return redirect("forbidden")

    role = get_object_or_404(Role, pk=pk)

    if request.method == "POST":
        role.delete()  # Eliminar el rol de la base de datos
        return redirect("role-list")

    # Si el método no es POST, mostrar la página de confirmación
    return render(request, "roles/role_confirm_delete.html", {"role": role})
