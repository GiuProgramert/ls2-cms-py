# Generated by Django 5.0.7 on 2024-09-22 14:34

from django.db import migrations
from roles.utils import PermissionEnum


def add_default_roles(apps, schema_editor):
    Permission = apps.get_model("roles", "Permission")
    Role = apps.get_model("roles", "Role")

    # Get the MODERAR_ARTICULOS permission
    moderar_articulos_perm = Permission.objects.get(
        name=PermissionEnum.MODERAR_ARTICULOS
    )

    # Update roles that should NOT have MODERAR_ARTICULOS permission
    roles_to_update = ["Autor", "Editor", "Suscriptor"]

    for role_name in roles_to_update:
        role = Role.objects.get(name=role_name)
        # Remove the MODERAR_ARTICULOS permission
        role.permissions.remove(moderar_articulos_perm)


class Migration(migrations.Migration):
    dependencies = [
        ("roles", "0005_add__permiso_editar_borrador"),
    ]

    operations = [
        migrations.RunPython(add_default_roles),
    ]