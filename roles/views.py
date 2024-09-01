from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import UpdateView
from django.contrib.auth.mixins import UserPassesTestMixin
from user.models import CustomUser,Role
from user.forms import RoleAssignmentForm

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
    template_name = 'roles/assign_roles.html'
    success_url = reverse_lazy('user-list')  # Cambia 'user-list' por el nombre correcto de tu URL

    def test_func(self):
        """
        Verifica si el usuario actual tiene permisos para acceder a la vista.

        Solo permite acceso a usuarios que sean superadministradores o que tengan el permiso
        específico para cambiar roles (`roles.change_role`).

        Returns:
            bool: True si el usuario tiene acceso; False en caso contrario.
        """

        return self.request.user.is_superuser or self.request.user.has_perm('roles.change_role')