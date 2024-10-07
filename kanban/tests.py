
from unittest.mock import patch, MagicMock
from article.models import Payment
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

# Create your tests here.


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
)
from article.forms import CategoryForm


User =  get_user_model()


class ArticleStatusChangeTest(TestCase):
    
    def setUp(self):
        # Crear un usuario para las pruebas
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpassword"
        )

        self.client = Client()
        self.client.login(username="testuser", password="testpassword")

        self.category = Category.objects.create(
            name="Test Category",
            description="Test Description",
            type=CategoryType.FREE.value,
            state=True,
            is_moderated=False,
        )

        
        # Crear un artículo en estado Borrador
        self.article = Article.objects.create(
            title='Artículo de Prueba',
            description='Este es el contenido del artículo.',
            category= self.category,
            state=ArticleStates.DRAFT.value,
            autor=self.user
        )

    
    def test_change_state_to_revision(self):
        """Probar el cambio de estado de 'Borrador' a 'Revisión'."""
        self.article.change_state(ArticleStates.REVISION.value)
        self.assertEqual(self.article.state, ArticleStates.REVISION.value)


    def test_change_state_to_edicion(self):
        """Probar el cambio de estado de 'Revisión' a 'Edición'."""
        self.article.change_state(ArticleStates.REVISION.value)  # Primero debe pasar a revisión
        self.article.change_state(ArticleStates.EDITED.value)  # Luego a edición
        self.assertEqual(self.article.state, ArticleStates.EDITED.value)


    def test_change_state_to_publicado(self):
        """Probar el cambio de estado de 'Edición' a 'Publicado'."""
        self.article.change_state(ArticleStates.REVISION.value)
        self.article.change_state(ArticleStates.EDITED.value)
        self.article.change_state(ArticleStates.PUBLISHED.value)  # Finalmente, el estado Publicado
        self.assertEqual(self.article.state, ArticleStates.PUBLISHED.value)


class StripeCheckoutTests(TestCase):


    def setUp(self):
        # Crear un usuario para las pruebas
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpassword"
        )

        self.client = Client()
        self.client.login(username="testuser", password="testpassword")

        self.category = Category.objects.create(
            name="Test Category",
            description="Test Description",
            type=CategoryType.FREE.value,
            state=True,
            is_moderated=False,
        )


    @patch('article.views.stripe.checkout.Session.create')
    def test_stripe_checkout(self, mock_stripe_session_create):
        """
        Test para la vista stripe_checkout.
        Simula la creación de una sesión de pago de Stripe y verifica la respuesta.
        """
        # Simular respuesta de Stripe
        mock_stripe_session = MagicMock(id='test_session_id')
        mock_stripe_session_create.return_value = mock_stripe_session

        # Llamar a la vista stripe_checkout
        response = self.client.get(reverse('stripe_checkout', args=[self.category.id]))

        # Verificar que la sesión de Stripe fue creada con los parámetros correctos
        mock_stripe_session_create.assert_called_once()
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'id': 'test_session_id'})

        # Verificar que se creó un Payment en la base de datos con estado 'pending'
        payment = Payment.objects.get(user=self.user, category=self.category)
        self.assertEqual(payment.status, 'pending')
        self.assertEqual(payment.stripe_payment_id, 'test_session_id')


    def test_checkout_page_completed_payment(self):
        """
        Test para verificar si un usuario ya ha completado un pago.
        """
        # Crear un pago completado
        Payment.objects.create(user=self.user, category=self.category, status='completed')

        # Llamar a la vista checkout_page
        response = self.client.get(reverse('checkout_page', args=[self.category.id]))

        # Verificar que redirige a la página 'exists.html'
        self.assertTemplateUsed(response, 'article/exists.html')



    def test_checkout_page_no_payment(self):
        """
        Test para verificar que se muestra el formulario de pago si no se ha completado ningún pago.
        """
        # Llamar a la vista checkout_page cuando no hay pagos
        response = self.client.get(reverse('checkout_page', args=[self.category.id]))

        # Verificar que se muestra la página 'checkout.html'
        self.assertTemplateUsed(response, 'article/checkout.html')
        self.assertEqual(response.context['STRIPE_PUBLISHABLE_KEY'], settings.STRIPE_PUBLIC_KEY)




    @patch('article.views.stripe.checkout.Session.retrieve')
    def test_payment_success(self, mock_stripe_session_retrieve):
        """
        Test para verificar que el pago se complete correctamente.
        """
        # Crear un pago pendiente
        payment = Payment.objects.create(user=self.user, category=self.category, status='pending', stripe_payment_id='test_session_id')

        # Simular respuesta de Stripe con estado 'complete'
        mock_stripe_intent = MagicMock(status='complete')
        mock_stripe_session_retrieve.return_value = mock_stripe_intent

        # Llamar a la vista payment_success
        response = self.client.get(reverse('payment_success', args=[self.category.id]))

        # Verificar que el pago se completó
        payment.refresh_from_db()
        self.assertEqual(payment.status, 'completed')
        self.assertTemplateUsed(response, 'article/success.html')


    

    def test_payment_cancel(self):
        """
        Test para verificar que un pago cancelado actualiza correctamente el estado.
        """
        # Crear un pago pendiente
        payment = Payment.objects.create(user=self.user, category=self.category, status='pending')

        # Llamar a la vista payment_cancel
        response = self.client.get(reverse('payment_cancel', args=[self.category.id]))

        # Verificar que el estado del pago se actualizó a 'cancelled'
        payment.refresh_from_db()
        self.assertEqual(payment.status, 'cancelled')
        self.assertTemplateUsed(response, 'article/cancel.html')





    #Verificar esta parte he'i
    # @patch('article.views.stripe.checkout.Session.create')
    # def test_stripe_checkout_unauthenticated(self, mock_stripe_session_create):
    #     """
    #     Test para la vista stripe_checkout con usuario no autenticado.
    #     Se espera que redirija a la página de inicio de sesión.
    #     """
    #     # Simular la creación de una sesión de Stripe (aunque no se debería llamar)
    #     mock_stripe_session = MagicMock(id='test_session_id')
    #     mock_stripe_session_create.return_value = mock_stripe_session

    #     # Llamar a la vista stripe_checkout sin autenticación
    #     response = self.client.get(reverse('stripe_checkout', args=[self.category.id]))

    #     # Verificar que el usuario fue redirigido a la página de inicio de sesión
    #     self.assertRedirects(response, reverse('login'))  # Asegúrate de que la URL de inicio de sesión es correcta
    #     # Verificar que no se creó un Payment en la base de datos
    #     self.assertEqual(Payment.objects.count(), 0)


    # def test_checkout_page_unauthenticated(self):
    #     """
    #     Test para verificar la vista checkout_page con usuario no autenticado.
    #     Se espera que redirija a la página de inicio de sesión.
    #     """
    #     # Llamar a la vista checkout_page sin autenticación
    #     response = self.client.get(reverse('checkout_page', args=[self.category.id]))

    #     # Verificar que el usuario fue redirigido a la página de inicio de sesión
    #     self.assertRedirects(response, reverse('login'))  # Asegúrate de que la URL de inicio de sesión es correcta

    # def test_payment_success_unauthenticated(self):
    #     """
    #     Test para verificar la vista payment_success con usuario no autenticado.
    #     Se espera que redirija a la página de inicio de sesión.
    #     """
    #     # Llamar a la vista payment_success sin autenticación
    #     response = self.client.get(reverse('payment_success', args=[self.category.id]))

    #     # Verificar que el usuario fue redirigido a la página de inicio de sesión
    #     self.assertRedirects(response, reverse('login'))  # Asegúrate de que la URL de inicio de sesión es correcta

    # def test_payment_cancel_unauthenticated(self):
    #     """
    #     Test para verificar la vista payment_cancel con usuario no autenticado.
    #     Se espera que redirija a la página de inicio de sesión.
    #     """
    #     # Llamar a la vista payment_cancel sin autenticación
    #     response = self.client.get(reverse('payment_cancel', args=[self.category.id]))

    #     # Verificar que el usuario fue redirigido a la página de inicio de sesión
    #     self.assertRedirects(response, reverse('login'))  # Asegúrate de que la URL de inicio de sesión es correcta


class ArticleLikeDislikeTest(TestCase):

    def setUp(self):
        # Crear usuario y categoría para los tests
        self.client = Client()
        self.user_can_manage_articles = User.objects.create_user(
            username="testuser", password="testpassword"
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

        # Crear categoría
        self.category = Category.objects.create(
            name="Test Category",
            description="Test Description",
            type=CategoryType.FREE.value,
            state=True,
            is_moderated=False,
        )

        # Crear artículo
        self.article = Article.objects.create(
            title='Artículo de Prueba',
            autor=self.user_can_manage_articles,
            description='Descripción del artículo de prueba.',
            category=self.category,
            state=ArticleStates.PUBLISHED.value
        )

    # def test_like_article(self):
    #     """Test que verifica que el usuario puede marcar un artículo como 'me gusta'."""
    #     self.client.login(username='testuser', password='testpassword')  # Cambia a la contraseña correcta
    #     url = reverse('like-article', args=[self.article.pk])

    #     # Realiza una solicitud POST para marcar el artículo como 'me gusta'
    #     response = self.client.post(url)

    #     # Refresca el artículo para obtener el valor actualizado
    #     self.article.refresh_from_db()
        
    #     # Verifica que el número de 'me gusta' se ha incrementado
    #     self.assertEqual(self.article.likes_number, 1)
    #     self.assertEqual(self.article.dislikes_number, 0)

    #     # Verificar que el voto se haya registrado
    #     vote = ArticleVote.objects.get(user=self.user_can_manage_articles, article=self.article)  # Cambia a self.user_can_manage_articles
    #     self.assertEqual(vote.vote, ArticleVote.LIKE)

    #     # Verifica que se redirige a la vista de detalle del artículo
    #     self.assertRedirects(response, reverse('article-detail', args=[self.article.pk]))