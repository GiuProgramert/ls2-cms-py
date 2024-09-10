from django.db import models
from django.contrib.auth import get_user_model
from enum import Enum
from mdeditor.fields import MDTextField

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

    def __str__(self):
        return self.name


class Article(models.Model):
    """
    Modelo que representa un artículo.

    Attributes:
        title (str): Título del artículo.
        description (str): Descripción del articulo
        autor (ForeignKey): Referencia al usuario autor del artículo.
        views_number (int): Número de visualizaciones del artículo.
        shares_number (int): Número de veces que se ha compartido el artículo.
        likes_number (int): Número de 'me gusta' que ha recibido el artículo.
        dislikes_number (int): Número de 'no me gusta' que ha recibido el artículo.
        category (ForeignKey): Referencia a la categoría a la que pertenece el artículo.
    """

    title = models.CharField(max_length=100)
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(max_length=300, null=True)

    views_number = models.IntegerField(default=0)
    shares_number = models.IntegerField(default=0)
    likes_number = models.IntegerField(default=0)
    dislikes_number = models.IntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


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
