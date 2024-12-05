from django.db import models
from django.contrib.auth import get_user_model
from enum import Enum
from mdeditor.fields import MDTextField
from notification.utils import send_email
from django.utils import timezone
from taggit.managers import TaggableManager

User = get_user_model()


class CategoryType(Enum):
    """
    Enumeración que define los tipos de artículos disponibles.

    Los valores posibles son:
    - FREE: Artículo gratuito que puede ser accedido por invitados.
    - PAY: Artículo que pertenece a una categoria de pago.
    - SUSCRIPTION: Artículo disponible por suscripción a una categoria.
    """

    FREE = "free"
    PAY = "pay"
    SUSCRIPTION = "suscription"


def get_state_name(state):
    """
    Obtiene el nombre del estado de un artículo.

    Args:
        state (str): El estado del artículo.

    Returns:
        str: El nombre del estado del artículo.
    """

    if state == ArticleStates.DRAFT.value:
        return "Borrador"
    if state == ArticleStates.REVISION.value:
        return "En revisión"
    if state == ArticleStates.EDITED.value:
        return "Editado"
    if state == ArticleStates.PUBLISHED.value:
        return "Publicado"
    if state == ArticleStates.INACTIVE.value:
        return "Inactivo"

    return "Desconocido"


class Category(models.Model):
    """
    Modelo que representa una categoría de artículos.

    Attributes:
        type_choices (list): Lista de opciones para el tipo de categoría, basada en la enumeración `ArticleType`.
        name (str): Nombre de la categoría.
        description (str): Descripción de la categoría.
        type (str): Tipo de categoría, definido por las opciones en `type_choices`.
        state (bool): Estado de la categoría, activa o inactiva.
        is_moderated (bool): Indica si la categoría requiere moderación.
    """

    type_choices = [
        (CategoryType.FREE.value, "Free"),
        (CategoryType.SUSCRIPTION.value, "Suscripción"),
        (CategoryType.PAY.value, "Pago"),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    type = models.CharField(choices=type_choices, default=CategoryType.FREE)
    state = models.BooleanField(default=True)
    is_moderated = models.BooleanField(default=False)
    price = models.FloatField(default=0.0, null=True)
    createdBy = models.IntegerField(null=True)  # Quita el valor predeterminado

    def has_purchased_category(self, user):
        """
        Verifica si el usuario ha comprado una categoría específica.

        Args:
            user (user): el usuario a verificar.

        Returns:
            bool: Retorna True si el usuario ha comprado la categoría, False si no.
        """
        return UserCategoryPurchase.objects.filter(user=user, category=self).exists()

    def __str__(self):
        return self.name


class FavoriteCategory(models.Model):
    """
    Modelo que representa la relación entre un usuario y sus categorías favoritas.

    Attributes:
        user (ForeignKey): Referencia al usuario que ha seleccionado una categoría como favorita.
        category (ForeignKey): Referencia a la categoría seleccionada como favorita por el usuario.

    Meta:
        unique_together (tuple): Evita la duplicación de combinaciones de usuario y categoría, asegurando que un usuario no pueda tener la misma categoría marcada como favorita más de una vez.
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="favorite_categories"
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "category")  # Evitar duplicados

    def __str__(self):
        return f"{self.user.username} - {self.category.name}"


class ArticleStates(Enum):
    """
    Enumeración que define los estados de un artículo.

    Los valores posibles son:
    - PENDING: Artículo pendiente de revisión.
    - APPROVED: Artículo aprobado.
    - REJECTED: Artículo rechazado.
    """

    DRAFT = "d"
    REVISION = "r"
    EDITED = "e"
    PUBLISHED = "p"
    INACTIVE = "i"


class Article(models.Model):
    """
    Modelo que representa un artículo.

    Attributes:
        title (str): Título del artículo.
        description (str): Descripción del articulo
        autor (ForeignKey): Referencia al usuario autor del artículo.
        tags (TaggableManager): Campo para manejar los etiquetas (tags).
        is_featured (Boolean): Campo para marcar como destacado a un articulo.
        views_number (int): Número de visualizaciones del artículo.
        shares_number (int): Número de veces que se ha compartido el artículo.
        likes_number (int): Número de 'me gusta' que ha recibido el artículo.
        dislikes_number (int): Número de 'no me gusta' que ha recibido el artículo.
        category (ForeignKey): Referencia a la categoría a la que pertenece el artículo.
    """

    title = models.CharField(max_length=100)
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(max_length=300, null=True)
    tags = TaggableManager()
    is_featured = models.BooleanField(default=False, verbose_name="¿Destacar este artículo?")

    views_number = models.IntegerField(default=0)
    shares_number = models.IntegerField(default=0)
    likes_number = models.IntegerField(default=0)
    dislikes_number = models.IntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    published_at = models.DateTimeField(
        auto_now_add=False, auto_now=False, null=True, default=None
    )
    state = models.CharField(
        max_length=1,
        choices=[
            (ArticleStates.DRAFT.value, "Borrador"),
            (ArticleStates.REVISION.value, "En revisión"),
            (ArticleStates.EDITED.value, "Editado"),
            (ArticleStates.PUBLISHED.value, "Publicado"),
            (ArticleStates.INACTIVE.value, "Inactivo"),
        ],
        default=ArticleStates.DRAFT.value,
    )

    def change_state(self, new_state):
        """
        Cambia el estado del artículo.

        Args:
            new_state (str): El nuevo estado del artículo.
        """

        send_email(
            to=self.autor.email,
            subject="CMS PY: Cambio de estado de artículo",
            html=f"""
                <h3>Hola, {self.autor.username}</h3>
                <p>
                    El esta de tu articulo <strong>{self.title}</strong> ha sido cambiado
                </p>
                <p>
                    <strong>{get_state_name(self.state)}</strong> → <strong>{get_state_name(new_state)}</strong>
                </p>
            """,
        )

        if new_state == ArticleStates.PUBLISHED.value:
            self.published_at = timezone.now()

        self.state = new_state
        self.save()


class ArticlesToPublish(models.Model):
    """
    Modelo que representa los artículos que están pendientes de publicación.

    Attributes:
        article (ForeignKey): Referencia al artículo que está pendiente de publicación.
        created_at (DateTimeField): Fecha de creación del registro.
    """

    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    to_publish_at = models.DateTimeField(null=False)
    published = models.BooleanField(default=False)


class ArticleContent(models.Model):
    """
    Modelo que representa el contenido del articulo

    Attibutes:
        body (str): campo que simboliza el contenido del articulo
        autor (str): campo que simboliza el autor que realizo el cambio en el contenido
        article (ForeignKey): Referencia al articulo
    """

    body = MDTextField()
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)


class UserCategoryPurchase(models.Model):
    """
    Modelo que representa una compra de categoría por un usuario.

    Attributes:
        user (ForeignKey): El usuario que realizó la compra.
        category (ForeignKey): La categoría que fue comprada.
        purchase_date (DateTimeField): Fecha de la compra.
        price (DecimalField): Precio de la categoría en el momento de la compra.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    purchase_date = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return (
            f"{self.user.username} compró {self.category.name} el {self.purchase_date}"
        )


class ArticleVote(models.Model):
    """
    Clase que representa el voto de un usuario en un artículo.
    
    Attributes:
        user (ForeignKey): El usuario que votó.
        article (ForeignKey): El artículo que recibió el voto.
        vote (IntegerField): El voto del usuario.
        rating (IntegerField): La calificación del usuario.
    """

    LIKE = 1
    DISLIKE = -1
    VOTE_CHOICES = [
        (LIKE, "Like"),
        (DISLIKE, "Dislike"),
    ]

    RATING_CHOICES = [
        (1, "1 Star"),
        (2, "2 Stars"),
        (3, "3 Stars"),
        (4, "4 Stars"),
        (5, "5 Stars"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    vote = models.IntegerField(choices=VOTE_CHOICES, null=True, blank=True)
    rating = models.IntegerField(choices=RATING_CHOICES, null=True, blank=True)

    class Meta:
        unique_together = ("user", "article")

    def __str__(self):
        return (
            f"{self.user.username} rated {self.article.title} with {self.rating} stars"
        )


class Payment(models.Model):
    """
    Modelo que representa un pago realizado por un usuario.

    Attributes:
        user (ForeignKey): El usuario que realizó el pago.
        category (ForeignKey): La categoría que fue comprada.
        price (DecimalField): Precio de la categoría en el momento de la compra.
        date_paid (DateTimeField): Fecha en la que se realizó el pago.
        stripe_payment_id (CharField): ID del pago en Stripe.
        status (CharField): Estado del pago.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.FloatField(default=0.00, null=True)
    date_paid = models.DateTimeField(default=timezone.now)
    stripe_payment_id = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=20, default="pending")  # Agregar este campo
