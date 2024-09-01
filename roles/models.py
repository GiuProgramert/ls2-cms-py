from django.db import models


class Permission(models.Model):
    """
    Modelo que representa un permiso específico dentro del sistema.

    Attributes:
        name (str): Nombre del permiso.
        description (str): Descripción detallada del permiso.
    """

    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


class Role(models.Model):
    """
    Modelo que representa un rol dentro del sistema.

    Un rol agrupa varios permisos que definen qué acciones puede realizar un usuario con este rol.

    Attributes:
        name (str): Nombre del rol.
        description (str): Descripción del rol.
        permissions (ManyToManyField): Relación de muchos a muchos con el modelo `Permission`, indicando los permisos asociados al rol.
    """

    name = models.CharField(max_length=100)
    description = models.TextField()
    permissions = models.ManyToManyField(Permission, related_name="roles")

    def __str__(self):
        return self.name
