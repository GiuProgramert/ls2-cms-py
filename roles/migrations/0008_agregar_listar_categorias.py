# Generated by Django 5.0.7 on 2024-11-02 14:26

from django.db import migrations
from roles.utils import PermissionEnum

def add_default_roles(apps, schema_editor):
    Permission = apps.get_model("roles", "Permission")
    Role = apps.get_model("roles", "Role")

    role_suscriptor = Role.objects.get(name="Suscriptor")

    Permission.objects.create(
        name=PermissionEnum.VER_CATEGORIAS,
        description="Permite ver las categorías disponibles en el sistema.",
    )

    role_suscriptor.permissions.add(
        Permission.objects.get(name=PermissionEnum.VER_CATEGORIAS),
    )


class Migration(migrations.Migration):

    dependencies = [
        ('roles', '0007_agregar_rol_financiero'),
    ]

    operations = [
        migrations.RunPython(add_default_roles),
    ]
