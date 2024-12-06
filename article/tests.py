from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from roles.models import Role
from roles.utils import PermissionEnum
from roles.models import Permission
from article.models import (
    Category,
    CategoryType,
    Article,
    ArticleContent,
    ArticleVote,
    ArticleStates,
    ArticlesToPublish,
)
from article.forms import CategoryForm
import warnings


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

    # def test_home_usuario_visitante(self):
    #     """
    #     Sí no es un usuario autenticado, no debe tener permisos

    #     Es correcto sí no se muestra la lista de permisos (ya que no los posee) y se obtiene la vista de home
    #     """

    #     self.client.logout()

    #     response = self.client.get(
    #         reverse("home"),
    #     )
    #     permisos = response.context["permisos"]

    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, "article/home.html")
    #     self.assertNotContains(response, "permisos")
    #     self.assertEqual(len(permisos), 0)


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

    # TODO check test function
    def test_crear_articulo_autenticado_sin_permiso(self):
        """
        Test para verificar que un usuario sin permisos no puede acceder a la vista

        Es correcto sí se redirige a la vista de forbidden
        """

        self.client.login(username="testuser", password="testpassword")
        self.role.permissions.remove(self.permission_crear_articulos)

        response = self.client.get(reverse("article-create"))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("forbidden"))

    # TODO check test function
    def test_crear_articulo_no_autenticado(self):
        """
        Test para verificar que un usuario no autenticado no puede acceder a la vista

        Es correcto sí se redirige a la vista de login
        """

        response = self.client.get(reverse("article-create"))

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
            "price": 0.0,
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
            "price": 0.0,
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


class PruebasGestionArticulo(TestCase):
    def setUp(self):
        """
        Inicializa la configuración de las pruebas.
        Crea un usuario, un rol, permisos, y una categoría para los tests.
        """
        self.client = Client()
        self.user_can_manage_articles = User.objects.create_user(
            username="articleuser", password="articlepassword"
        )

        # Crear rol y permisos
        self.role = Role.objects.create(name="ArticleManagerRole")
        self.permission_crear_articulos = Permission.objects.create(
            name=PermissionEnum.CREAR_ARTICULOS
        )
        self.permission_editar_articulos = Permission.objects.create(
            name=PermissionEnum.EDITAR_ARTICULOS
        )
        self.permission_ver_articulos = Permission.objects.create(
            name=PermissionEnum.VER_INICIO
        )

        # Añadir permisos al rol
        self.role.permissions.add(
            self.permission_crear_articulos,
            self.permission_editar_articulos,
            self.permission_ver_articulos,
        )

        # Asignar rol al usuario
        self.user_can_manage_articles.roles.add(self.role)

        # Crear una categoría
        self.category = Category.objects.create(
            name="Test Category",
            description="A test category",
            type=CategoryType.FREE.value,
            state=True,
            is_moderated=False,
        )

        # Crear un artículo
        self.article = Article.objects.create(
            title="Test Article",
            autor=self.user_can_manage_articles,
            category=self.category,
            description="A description for the test article",
        )

        ArticleContent.objects.create(
            article=self.article,
            body="Test Article Content",
            autor=self.user_can_manage_articles,
        )

    def test_crear_articulo_autenticado_con_permiso(self):
        """
        Verificar que un usuario con permiso 'CREAR_ARTICULOS' puede crear un artículo.
        """
        self.client.login(username="articleuser", password="articlepassword")

        data = {
            "title": "New Article",
            "description": "This is a new article",
            "category": self.category.id,  # ID de categoría válido
            "body": "This is the content of the new article",
            "tags": "tag1, tag2, tag3",
        }

        response = self.client.post(reverse("article-create"), data)

        new_article = Article.objects.get(title="New Article")

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Article.objects.filter(title="New Article").exists())
        self.assertRedirects(response, reverse("article-detail", args=[new_article.pk]))

    def test_crear_articulo_autenticado_sin_permiso(self):
        """
        Verificar que un usuario sin permiso 'CREAR_ARTICULOS' es redirigido.
        """
        self.role.permissions.remove(self.permission_crear_articulos)
        self.client.login(username="articleuser", password="articlepassword")

        response = self.client.get(reverse("article-create"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("forbidden"))

    def test_actualizar_articulo_autenticado_con_permiso(self):
        """
        Verificar que un usuario con permiso 'EDITAR_ARTICULOS' puede actualizar un artículo.
        """
        self.client.login(username="articleuser", password="articlepassword")

        data = {
            "title": "Updated Title",
            "description": "Updated description",
            "category": self.category.id,
            "body": "Updated article content",
            "tags": "tag1, tag2, tag3",
        }

        response = self.client.post(
            reverse("article-update", args=[self.article.pk]), data
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse("article-detail", args=[self.article.pk])
        )

        # Verificar que el artículo fue actualizado
        self.article.refresh_from_db()
        self.assertEqual(self.article.title, "Updated Title")

    def test_actualizar_articulo_autenticado_sin_permiso(self):
        """
        Verificar que un usuario sin permiso 'EDITAR_ARTICULOS' es redirigido.
        """
        self.role.permissions.remove(self.permission_editar_articulos)
        self.client.login(username="articleuser", password="articlepassword")

        response = self.client.get(reverse("article-update", args=[self.article.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("forbidden"))

    def test_historial_articulo_autenticado_con_permiso(self):
        """
        Verificar que un usuario con permiso 'EDITAR_ARTICULOS' puede ver el historial de un artículo.
        """
        self.client.login(username="articleuser", password="articlepassword")
        response = self.client.get(
            reverse("article-update-history", args=[self.article.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "article/article_update_history.html")

    def test_historial_articulo_autenticado_sin_permiso(self):
        """
        Verificar que un usuario sin permiso 'EDITAR_ARTICULOS' es redirigido.
        """

        self.role.permissions.remove(self.permission_editar_articulos)

        self.client.login(username="articleuser", password="articlepassword")

        new_user = User.objects.create_user(
            username="articleuser2", password="articlepassword2"
        )

        self.article.autor = new_user
        self.article.save()

        response = self.client.get(
            reverse("article-update-history", args=[self.article.pk])
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("forbidden"))

    def test_listar_articulos_autenticado_con_permiso(self):
        """
        Verificar que un usuario con permiso 'VER_INICIO' puede ver la lista de artículos.
        """
        self.client.login(username="articleuser", password="articlepassword")
        response = self.client.get(reverse("article-list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "article/article_list.html")

    def test_listar_articulos_autenticado_sin_permiso(self):
        """
        Verificar que un usuario sin permiso 'VER_INICIO' es redirigido.
        """
        self.role.permissions.remove(self.permission_ver_articulos)
        self.client.login(username="articleuser", password="articlepassword")
        response = self.client.get(reverse("article-list"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("forbidden"))

    def test_detalle_articulo_autenticado_con_permiso(self):
        """
        Verificar que un usuario con permiso 'VER_INICIO' puede ver los detalles de un artículo.
        """
        self.client.login(username="articleuser", password="articlepassword")
        response = self.client.get(reverse("article-detail", args=[self.article.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "article/article_detail.html")

    def test_detalle_articulo_autenticado_sin_permiso(self):
        """
        Verificar que un usuario sin permiso 'VER_INICIO' es redirigido.
        """
        self.role.permissions.remove(self.permission_ver_articulos)
        self.client.login(username="articleuser", password="articlepassword")
        response = self.client.get(reverse("article-detail", args=[self.article.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("forbidden"))

    def test_compartir_articulo(self):
        """
        Prueba para compartir un artículo. El contador de compartidos debe subir
        """

        self.client.login(username="articleuser", password="articlepassword")
        response = self.client.get(f"/article/{self.article.pk}/detail/?shared=true")

        self.assertEqual(self.article.shares_number, 0)

        self.article.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.article.shares_number, 1)

    def test_programar_publicacion_articulo_autenticado_con_permiso(self):
        """
        Verifica que un usuario con permiso pueda programar la publicación de un artículo.
        """
        self.client.login(username="articleuser", password="articlepassword")
        data = {"to_publish_date": "2024-12-01 10:00:00"}

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            response = self.client.post(
                reverse("article-to-published-schedule", args=[self.article.pk]), data
            )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse("article-detail", args=[self.article.pk])
        )
        self.assertTrue(ArticlesToPublish.objects.filter(article=self.article).exists())
    
    def test_descargar_categorías_vendidas_suscriptor_autenticado_con_permiso(self):
        """
        Prueba que un usuario con los permisos adecuados pueda descargar las categorías vendidas como suscriptor.
        """
        self.client.login(username="articleuser", password="articlepassword")
        self.user_can_manage_articles.roles.add(self.role)

        # Ensure the user can log in
        login_successful = self.client.login(username="articleuser", password="articlepassword")
        self.assertTrue(login_successful)
        
        self.permission_ver_categorias = Permission.objects.create(
            name=PermissionEnum.VER_CATEGORIAS
        )
        
        self.role.permissions.add(
            self.permission_ver_categorias,
        )
        
        response = self.client.get(reverse("download-sold-categories-suscriptor"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        self.assertIn("attachment", response["Content-Disposition"])
        self.assertTrue(response.content)  # Ensure the response has file content



class CasoDePruebaVotoArticulo(TestCase):
    """
    Pruebas para dar 'me gusta' y 'no me gusta' a artículos utilizando los modelos proporcionados en codigo3 y el modelo CustomUser.
    """

    def setUp(self):
        """
        Configura el cliente de prueba, usuario, categoría y artículos usando los modelos de codigo3 y el modelo CustomUser.
        """
        self.client = Client()

        # Crear usuario con el modelo CustomUser y asignarle un rol
        self.user = User.objects.create_user(
            username="votante", password="password", phone="123456789"
        )
        self.user.roles.add(Role.objects.get(name="Administrador"))

        # Crear categoría
        self.category = Category.objects.create(
            name="Categoría de Prueba",
            description="Esta es una categoría de prueba",
            type=CategoryType.FREE.value,
            state=True,
            is_moderated=False,
        )

        # Crear artículo
        self.article = Article.objects.create(
            title="Artículo de Prueba",
            autor=self.user,  # Usando el modelo CustomUser
            description="Esta es una descripción para el artículo de prueba",
            category=self.category,
            state=ArticleStates.PUBLISHED.value,  # Configurando el estado del artículo como publicado
        )

        ArticleContent.objects.create(
            article=self.article,
            body="Contenido del Artículo de Prueba",
            autor=self.user,
        )

        # Iniciar sesión del usuario
        self.client.login(username="votante", password="password")

    def test_me_gusta_articulo(self):
        """
        Prueba para dar 'me gusta' a un artículo.
        """
        response = self.client.get(reverse("like-article", args=[self.article.pk]))
        self.article.refresh_from_db()
        vote = ArticleVote.objects.get(article=self.article, user=self.user)

        self.assertEqual(self.article.likes_number, 1)
        self.assertEqual(vote.vote, ArticleVote.LIKE)
        self.assertRedirects(
            response, reverse("article-detail", args=[self.article.pk])
        )

    def test_no_me_gusta_articulo(self):
        """
        Prueba para dar 'no me gusta' a un artículo.
        """
        response = self.client.get(reverse("dislike-article", args=[self.article.pk]))
        self.article.refresh_from_db()
        vote = ArticleVote.objects.get(article=self.article, user=self.user)

        self.assertEqual(self.article.dislikes_number, 1)
        self.assertEqual(vote.vote, ArticleVote.DISLIKE)
        self.assertRedirects(
            response, reverse("article-detail", args=[self.article.pk])
        )


class CategoriasCompradas(TestCase):
    def setUp(self):
        """
        Inicializa la configuración de las pruebas
        """

        self.client = Client()
        self.user_can_create = User.objects.create_user(
            username="testuser", password="testpassword"
        )

        self.role = Role.objects.get(name="Suscriptor")

        self.user_can_create.roles.add(self.role)

        self.client.login(
            username="testuser",
            password="testpassword"
        )

    def test_view_requires_login(self):
        """
        Test para verificar que se requiere login para acceder
        """

        self.client.logout()
        response = self.client.get(reverse("sold-categories-suscriptor"))
        self.assertEqual(response.status_code, 302)

    def test_require_ver_categorias(self):
        """
        Verifica sí el usuario tiene el permiso "VER_CATEOGIAS"
        """

        permission = Permission.objects.get(name=PermissionEnum.VER_CATEGORIAS)
        self.role.permissions.remove(permission)

        response = self.client.get(reverse("sold-categories-suscriptor"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("forbidden"))

    def test_default_view_parameters(self):
        """
        Test Para ver que trae todos los parametros necesarios para generar el gráfico
        """
        response = self.client.get(reverse('sold-categories-suscriptor'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'article/sold_categories_suscriptor.html')

        # Check context data
        self.assertIn('payments', response.context)
        self.assertIn('payments_prices', response.context)
        self.assertIn('categories', response.context)
        self.assertIn('total_general', response.context)
