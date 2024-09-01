from django.db import models
from django.contrib.auth import get_user_model
from enum import Enum

User = get_user_model()


class CategoryType(Enum):
    FREE = "free"
    PAY = "pay"
    SUSCRIPTION = "suscription"


class Category(models.Model):
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
    title = models.CharField(max_length=100)
    autor = models.ForeignKey(User, on_delete=models.CASCADE)

    views_number = models.IntegerField(default=0)
    shares_number = models.IntegerField(default=0)
    likes_number = models.IntegerField(default=0)
    dislikes_number = models.IntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
