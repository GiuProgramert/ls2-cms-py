from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from roles.models import Role


class CustomUser(AbstractUser):
    """
    Modelo personalizado de usuario que extiende el modelo `AbstractUser` de Django.

    Incluye la relación de compras de categorías de pago.
    """

    phone = models.CharField(max_length=20)
    roles = models.ManyToManyField(Role)

    # Relación con las categorías compradas
    # purchased_categories = models.ManyToManyField(
    #    'article.Category', through='article.UserCategoryPurchase', related_name='users_who_purchased'
    # )
    is_active = models.BooleanField(
        default=True
    )  # This field manages whether the user is active or not
    # Necesario para evitar errores django
    groups = models.ManyToManyField(
        Group,
        related_name="customuser_set",  # Add related_name to avoid clash
        blank=True,
        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
        related_query_name="customuser",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="customuser_set",  # Add related_name to avoid clash
        blank=True,
        help_text="Specific permissions for this user.",
        related_query_name="customuser",
    )

    def tiene_permisos(self, permisos: list[str]) -> bool:
        """
        Verifica si el usuario tiene todos los permisos especificados.

        Args:
            permisos (list[str]): Lista de nombres de permisos a verificar.

        Returns:
            bool: Retorna `True` si el usuario tiene todos los permisos, de lo contrario `False`.
        """
        con_permiso = True

        for permiso in permisos:
            if not self.roles.filter(permissions__name=permiso).exists():
                con_permiso = False

        return con_permiso
