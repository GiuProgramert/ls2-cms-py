from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from roles.models import Role
from roles.utils import PermissionEnum
from roles.models import Permission
from article.models import Category, CategoryType
from article.forms import CategoryForm

User = get_user_model()


class HomeViewTest(TestCase):
    """
    Casos de prueba para la vista home
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

    def test_home_usuario_autenticado(self):
        """
        Sí es un usuario autenticado, debe tener permisos

        Es correcto sí se muestra la lista de permisos y se obtiene la vista de home
        """

        response = self.client.get(
            reverse("home"),
        )
        permisos = response.context["permisos"]

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "article/home.html")
        self.assertNotEqual(len(permisos), 0)

    def test_home_usuario_visitante(self):
        """
        Sí no es un usuario autenticado, no debe tener permisos

        Es correcto sí no se muestra la lista de permisos (ya que no los posee) y se obtiene la vista de home
        """

        self.client.logout()

        response = self.client.get(
            reverse("home"),
        )
        permisos = response.context["permisos"]

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "article/home.html")
        self.assertNotContains(response, "permisos")
        self.assertEqual(len(permisos), 0)


class CreateArticleTestCase(TestCase):
    """
    Casos de prueba para la vista home
    """

    def setUp(self):
        """
        Inicializa la configuración de las pruebas
        """

        self.client = Client()
        self.user_can_create = User.objects.create_user(
            username="testuser", password="testpassword"
        )

        self.role = Role.objects.create(name="Test Role")
        self.permission_crear_articulos = Permission.objects.create(
            name=PermissionEnum.CREAR_ARTICULOS
        )
        self.permission_manejar_categorias = Permission.objects.create(
            name=PermissionEnum.MANEJAR_CATEGORIAS
        )

        self.role.permissions.add(
            self.permission_crear_articulos, self.permission_manejar_categorias
        )

        self.user_can_create.roles.add(self.role)

        self.category = Category.objects.create(
            name="Test Category",
            description="Test Description",
            type=CategoryType.FREE.value,
            state=True,
            is_moderated=False,
        )

    def test_crear_articulo_autenticado_con_permiso(self):
        """
        Test para verificar que un usuario con permisos puede acceder a la vista

        Es correcto sí se redirige a la vista de create_article
        """

        self.client.login(username="testuser", password="testpassword")

        response = self.client.get(reverse("create-article"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "article/create_article.html")

    def test_crear_articulo_autenticado_sin_permiso(self):
        """
        Test para verificar que un usuario sin permisos no puede acceder a la vista

        Es correcto sí se redirige a la vista de forbidden
        """

        self.client.login(username="testuser", password="testpassword")
        self.role.permissions.remove(self.permission_crear_articulos)

        response = self.client.get(reverse("create-article"))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("forbidden"))

    def test_crear_articulo_no_autenticado(self):
        """
        Test para verificar que un usuario no autenticado no puede acceder a la vista

        Es correcto sí se redirige a la vista de login
        """

        response = self.client.get(reverse("create-article"))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("login"))

    def test_listar_categorias_autenticado_con_permiso(self):
        """
        Test para verificar que un usuario autenticado con permisos puede acceder a la vista de category_list

        Es correcto sí se obtiene la vista de category_list
        """

        self.client.login(username="testuser", password="testpassword")

        response = self.client.get(reverse("category-list"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "article/category_list.html")
        self.assertContains(response, self.category.name)

    def test_listar_categorias_autenticado_sin_permiso(self):
        """
        Test para verificar que un usuario autenticado sin permisos no puede acceder a la vista de category_list

        Es correcto sí se redirige a la vista de forbidden
        """
        self.role.permissions.remove(self.permission_manejar_categorias)
        self.client.login(username="testuser", password="testpassword")

        response = self.client.get(reverse("category-list"))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("forbidden"))

    def test_listar_categorias_no_autenticado(self):
        """
        Test para verificar que un usuario no autenticado no puede acceder a la vista de category_list

        Es correcto sí se redirige a la vista de login
        """

        response = self.client.get(reverse("category-list"))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("login"))

    def test_detalle_categoria_autenticado_con_permiso(self):
        """
        Test para verificar que un usuario autenticado puede acceder a la vista de category_detail

        Es correcto sí se obtiene la vista de category_detail
        """

        self.client.login(username="testuser", password="testpassword")

        response = self.client.get(reverse("category-detail", args=[self.category.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["category"], self.category)

    def test_detalle_categoria_autenticado_sin_permiso(self):
        """
        Test para verificar que un usuario autenticado sin permisos no puede acceder a la vista de category_detail
        """

        self.role.permissions.remove(self.permission_manejar_categorias)
        self.client.login(username="testuser", password="testpassword")

        response = self.client.get(reverse("category-detail", args=[self.category.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("forbidden"))

    def test_detalle_categoria_no_autenticado(self):
        """
        Test para verificar que un usuario no autenticado no puede acceder a la vista de category_detail
        """

        response = self.client.get(reverse("category-detail", args=[self.category.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("login"))

    def test_detalle_categoria_no_existente(self):
        """
        Test para verificar que un usuario no puede acceder a la vista de category_detail si la categoría no existe
        """

        self.client.login(username="testuser", password="testpassword")

        response = self.client.get(reverse("category-detail", args=[99999]))

        self.assertEqual(response.status_code, 404)

    def test_creacion_categoria_autenticado_con_permiso(self):
        """
        Test para verificar que se puede acceder a la vista de creación de categoría
        """
        self.client.login(username="testuser", password="testpassword")

        response = self.client.get(reverse("category-create"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "article/category_form.html")
        self.assertIsInstance(response.context["form"], CategoryForm)

    def test_creacion_categoria_autenticado_sin_permiso(self):
        """
        Test para verificar que un usuario sin permisos no puede acceder a la vista de creación de categoría
        """

        self.role.permissions.remove(self.permission_manejar_categorias)
        self.client.login(username="testuser", password="testpassword")

        response = self.client.get(reverse("category-create"))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("forbidden"))

    def test_creacion_categoria_no_autenticado(self):
        """
        Test para verificar que un usuario no autenticado no puede acceder a la vista de creación de categoría
        """

        response = self.client.get(reverse("category-create"))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("login"))

    def test_creacion_categoria_correctamente(self):
        """
        Test para verificar que se puede crear una categoría correctamente
        """

        data = {
            "name": "Test Category",
            "description": "This is a test category",
            "type": CategoryType.FREE.value,
            "state": True,
            "is_moderated": False,
        }

        self.client.login(username="testuser", password="testpassword")

        response = self.client.post(reverse("category-create"), data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("category-list"))
        self.assertTrue(Category.objects.filter(name="Test Category").exists())

    def test_creacion_categoria_form_invalido(self):
        """
        Test para verificar que no se puede crear una categoría con un formulario inválido
        """

        data = {
            "name": "",
            "description": "This is a test category",
        }

        self.client.login(username="testuser", password="testpassword")
        response = self.client.post(reverse("category-create"), data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "article/category_form.html")
        self.assertIsInstance(response.context["form"], CategoryForm)
        self.assertNotEqual(len(response.context["form"].errors), 0)

    def test_actualizar_categoria_vista(self):
        """
        Test para verificar que se puede acceder a la vista de actualización de categoría
        """

        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(reverse("category-update", args=[self.category.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "article/category_form.html")
        self.assertIsInstance(response.context["form"], CategoryForm)
        self.assertEqual(response.context["form"].instance, self.category)

    def test_actualizar_categoria_get(self):
        """
        Test para verificar que se puede actualizar una categoría con el método GET
        """

        data = {
            "name": "Updated Category",
            "description": "Updated Description",
            "type": CategoryType.FREE.value,
            "state": True,
            "is_moderated": False,
        }

        self.client.login(username="testuser", password="testpassword")
        response = self.client.post(
            reverse("category-update", args=[self.category.pk]), data
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("category-list"))

        self.category.refresh_from_db()

        self.assertEqual(self.category.name, "Updated Category")

    def test_actualizar_categoria_post_form_invalido(self):
        """
        Test para verificar que no se puede actualizar una categoría con un formulario inválido
        """

        data = {"name": ""}

        self.client.login(username="testuser", password="testpassword")
        response = self.client.post(
            reverse("category-update", args=[self.category.pk]), data
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "article/category_form.html")
        self.assertIsInstance(response.context["form"], CategoryForm)
        self.assertEqual(response.context["form"].instance, self.category)
        self.assertNotEqual(len(response.context["form"].errors), 0)

    def test_eliminacion_categoria_usuario_autenticado_con_permiso(self):
        """
        Test para verificar que un usuario autenticado con permisos puede eliminar una categoría
        """

        self.client.login(username="testuser", password="testpassword")

        response = self.client.post(reverse("category-delete", args=[self.category.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("category-list"))
        self.assertFalse(Category.objects.filter(pk=self.category.pk).exists())

    def test_eliminacion_categoria_usuario_sin_permiso(self):
        """
        Test para verificar que un usuario autenticado sin permisos no puede eliminar una categoría
        """

        self.role.permissions.remove(self.permission_manejar_categorias)
        self.client.login(username="testuser", password="testpassword")

        response = self.client.post(reverse("category-delete", args=[self.category.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("forbidden"))
        self.assertTrue(Category.objects.filter(pk=self.category.pk).exists())

    def test_eliminacion_categoria_sin_autentificacion(self):
        response = self.client.post(reverse("category-delete", args=[self.category.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("login"))
        self.assertTrue(Category.objects.filter(pk=self.category.pk).exists())
