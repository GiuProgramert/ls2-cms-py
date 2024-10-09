# Generated by Django 5.0.7 on 2024-10-06 16:12

from django.db import migrations
from roles.utils import PermissionEnum


def add_default_roles(apps, schema_editor):
    Permission = apps.get_model("roles", "Permission")
    Role = apps.get_model("roles", "Role")

    ver_categorias_pago = Permission.objects.get(
        name=PermissionEnum.VER_CATEGORIAS_PAGO
    )

    role = Role.objects.get(name="Publicador")
    role.permissions.remove(ver_categorias_pago)

    # crear el rol de financiero
    Role.objects.create(
        name="Financiero",
        description="Rol de financiero con privilegios de ver todo lo que el cms vendio",
    )

    # asignarle el rol de ver categorias de pago
    Role.objects.get(name="Financiero").permissions.add(
        Permission.objects.get(name=PermissionEnum.VER_CATEGORIAS_PAGO),
    )


class Migration(migrations.Migration):
    dependencies = [
        ("roles", "0006_corregir_permiso_moderar"),
    ]

    operations = [
        migrations.RunPython(add_default_roles),
    ]