from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

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
