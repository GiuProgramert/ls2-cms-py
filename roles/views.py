from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import UpdateView
from django.contrib.auth.mixins import UserPassesTestMixin
from user.models import CustomUser
from user.forms import RoleAssignmentForm
from roles.utils import PermissionEnum


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
