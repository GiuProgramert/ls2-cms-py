from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from roles.models import Role


class CustomUser(AbstractUser):
    """ """

    phone = models.CharField(max_length=20)
    roles = models.ManyToManyField(Role)

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
        Chequea si el usuario tiene permisos

        Args:
            permisos (list[str]): lista de permisos a chequear

        Returns:
            bool: Retorna True si el usuario tiene todos los permisos, False en caso contrario
        """

        con_permiso = True

        for permiso in permisos:
            if not self.roles.filter(permissions__name=permiso).exists():
                con_permiso = False

        return con_permiso
