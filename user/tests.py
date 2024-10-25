from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
import copy

User = get_user_model()


class LoginViewTestCase(TestCase):
    def setUp(self):
        """
        Inicializamos las variables que vamos a usar en los tests
        """

        self.client = Client()
        self.login_url = reverse("login")
        self.home_url = reverse("home")
        self.username = "testuser"
        self.password = "testpassword"
        self.user = User.objects.create_user(
            username=self.username, password=self.password
        )

    def test_login_view_with_valid_credentials(self):
        response = self.client.post(
            self.login_url, {"username": self.username, "password": self.password}
        )

        self.assertRedirects(response, self.home_url)

    def test_login_view_with_invalid_credentials(self):
        response = self.client.post(
            self.login_url, {"username": self.username, "password": "wrongpassword"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nombre de usuario o contraseña incorrecta")

    def test_login_view_with_get_request(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "user/login.html")


class RegisterViewTestCase(TestCase):
    def setUp(self):
        """
        Inicializamos las variables que vamos a usar en los tests
        """
        self.register_url = reverse("register")
        self.home_url = reverse("home")

        self.user_data = {
            "username": "testuser",
            "email": "user@fakeemail.com",
            "password1": "SuperSecret123",
            "password2": "SuperSecret123",
        }

    def test_register_view_with_valid_credentials(self):
        response = self.client.post(self.register_url, self.user_data)

        self.assertRedirects(response, self.home_url)

        # Validar se creo el usuario en la base de datos
        User = get_user_model()
        user_instance = User.objects.get(username=self.user_data["username"])
        self.assertIsNotNone(user_instance)
        self.assertEqual(user_instance.email, self.user_data["email"])

    def test_register_view_with_invalid_passwords(self):
        user_data_copy = copy.deepcopy(self.user_data)
        user_data_copy["password2"] = "DifferentPassword123"
        response = self.client.post(self.register_url, user_data_copy)

        self.assertEqual(response.status_code, 200)

    def test_register_missing_username(self):
        user_data_copy = copy.deepcopy(self.user_data)
        user_data_copy["username"] = ""
        response = self.client.post(self.register_url, user_data_copy)

        self.assertEqual(response.status_code, 200)

    def test_register_invalid_email(self):
        user_data_copy = copy.deepcopy(self.user_data)
        user_data_copy["email"] = "invalid-email"
        response = self.client.post(self.register_url, user_data_copy)

        self.assertEqual(response.status_code, 200)

    def test_register_existing_username(self):
        # Crear un nuevo usuario
        User = get_user_model()
        User.objects.create_user(
            username=self.user_data["username"],
            email="example@example.com",
            password="verySecurePassword123",
        )

        # Registar un nuevo usuario con el mismo nombre
        response = self.client.post(self.register_url, self.user_data)

        self.assertEqual(response.status_code, 200)
