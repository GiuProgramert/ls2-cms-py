from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import UpdateView
from django.contrib.auth.mixins import UserPassesTestMixin
from user.models import CustomUser,Role
from user.forms import RoleAssignmentForm

# Create your views here.
class RoleAssignmentView(UserPassesTestMixin, UpdateView):
    model = CustomUser
    form_class = RoleAssignmentForm
    template_name = 'roles/assign_roles.html'
    success_url = reverse_lazy('user-list')  # Cambia 'user-list' por el nombre correcto de tu URL

    def test_func(self):
        # Solo permite acceso a usuarios superadministradores o con permisos específicos
        return self.request.user.is_superuser or self.request.user.has_perm('roles.change_role')