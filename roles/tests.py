from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from roles.models import Role, Permission

User = get_user_model()


class RoleAssignmentViewTest(TestCase):
    """
    Casos de prueba para la vista RoleAssignmentView
    """

    def setUp(self):
        """
        Inicializa la configuración de las pruebas
        """

        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpassword"
        )

        self.user.roles.add(Role.objects.get(name="Administrador"))

        self.client.login(username="testuser", password="testpassword")

    def test_role_assignment_view_access(self):
        """
        Prueba si un usuario con el rol 'Administrador' puede acceder a la vista RoleAssignmentView
        """
        response = self.client.get(reverse("assign_roles", kwargs={"pk": self.user.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "roles/assign_roles.html")

    def test_role_assignment_success(self):
        """
        Prueba si el rol 'Administrador' puede ser asignado exitosamente a un usuario
        """
        role_to_assign = Role.objects.get(name="Administrador")
        response = self.client.post(
            reverse("assign_roles", kwargs={"pk": self.user.pk}),
            {"roles": [role_to_assign.id]},
        )

        self.user.refresh_from_db()
        self.assertIn(role_to_assign, self.user.roles.all())
        self.assertRedirects(response, reverse("user-list"))


class RoleModelTest(TestCase):
    """
    Casos de prueba para los modelos Role y Permission
    """

    def setUp(self):
        """
        Inicializa la configuración de las pruebas
        """
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpassword"
        )

        self.user.roles.add(Role.objects.get(name="Administrador"))

        self.permission = Permission.objects.get(name="manejo_roles")
        self.role = Role.objects.get(name="Administrador")

    def test_permission_creation(self):
        """
        Prueba si un permiso puede ser recuperado exitosamente
        """
        self.assertEqual(self.permission.name, "manejo_roles")
        self.assertEqual(str(self.permission), "manejo_roles")

    def test_role_creation(self):
        """
        Prueba si un rol puede ser recuperado exitosamente y está asociado con los permisos correctos
        """
        self.assertEqual(self.role.name, "Administrador")
        self.assertIn(self.permission, self.role.permissions.all())
        self.assertEqual(str(self.role), "Administrador")
