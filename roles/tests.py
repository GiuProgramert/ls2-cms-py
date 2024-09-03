# Create your tests here.
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

        # Create a superuser for testing
        self.superuser = User.objects.create_superuser(
            username="superuser",
            email="superuser@example.com",
            password="superpassword",
        )

        # Create a regular user
        self.user = User.objects.create_user(
            username="testuser", email="testuser@example.com", password="testpassword"
        )

        # Create roles and permissions
        self.permission = Permission.objects.create(
            name="Can change role", description="Permission to change roles"
        )
        self.role = Role.objects.create(
            name="Test Role", description="A role for testing"
        )
        self.role.permissions.add(self.permission)

        self.client.login(username="superuser", password="superpassword")

    def test_role_assignment_view_access(self):
        """
        Prueba si un superusuario puede acceder a la vista RoleAssignmentView
        """
        response = self.client.get(reverse("assign_roles", kwargs={"pk": self.user.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "roles/assign_roles.html")

    def test_role_assignment_without_permission(self):
        """
        Prueba si un usuario sin permisos no puede acceder a la vista RoleAssignmentView
        """
        self.client.logout()
        self.client.login(username="testuser", password="testpassword")

        response = self.client.get(reverse("assign_roles", kwargs={"pk": self.user.pk}))
        self.assertEqual(response.status_code, 302)  # Check for redirect
        self.assertRedirects(
            response, reverse("forbidden")
        )  # Verify redirect to forbidden page

    def test_role_assignment_success(self):
        """
        Prueba si un rol puede ser asignado exitosamente a un usuario
        """
        response = self.client.post(
            reverse("assign_roles", kwargs={"pk": self.user.pk}),
            {"roles": [self.role.id]},
        )

        self.user.refresh_from_db()
        self.assertIn(self.role, self.user.roles.all())
        self.assertRedirects(response, reverse("user-list"))
