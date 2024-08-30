from django.shortcuts import render, redirect
from roles.utils import PermissionEnum


def home(request):
    if not request.user.is_authenticated:
        tus_permisos = []
    else:
        tus_permisos = [
            permiso
            for rol in request.user.roles.all()
            for permiso in rol.permissions.all()
        ]

    return render(
        request,
        "article/home.html",
        {
            "permisos": tus_permisos,
        },
    )


def forbidden(request):
    return render(request, "article/forbidden.html")


def create_article(request):
    if not request.user.is_authenticated:
        return redirect("login")

    if not request.user.tiene_permisos([PermissionEnum.CREAR_ARTICULOS]):
        return redirect("forbidden")

    return render(request, "article/create_article.html")
