import mistune
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest
from roles.utils import PermissionEnum
from article.models import (
    Category,
    ArticleContent,
    Article,
    ArticleStates,
    CategoryType,
)
from article.forms import CategoryForm, ArticleForm


def home(request):
    """
    Vista que muestra la página principal del artículo.

    Si el usuario está autenticado, se recopilan los permisos que tiene
    y se envían al contexto de la plantilla. Si no está autenticado,
    se envía una lista vacía de permisos.

    Args:
        request (HttpRequest): La solicitud HTTP.

    Returns:
        HttpResponse: Renderiza la plantilla 'article/home.html'.
    """

    categories = Category.objects.all()

    if not request.user.is_authenticated:
        permissions = []

        permited_categories = [
            category
            for category in categories
            if category.type == CategoryType.FREE.value
        ]

        not_permited_categories = [
            {"name": category.name, "type": category.type}
            for category in categories
            if category.type != CategoryType.FREE.value
        ]
    else:
        permissions = [
            permiso.name
            for rol in request.user.roles.all()
            for permiso in rol.permissions.all()
        ]

        permited_categories = [
            category
            for category in categories
            if category.type
            in (CategoryType.FREE.value, CategoryType.SUSCRIPTION.value)
        ]

        not_permited_categories = [
            {"name": category.name, "type": category.type}
            for category in categories
            if category.type == CategoryType.PAY.value
        ]

    articles = Article.objects.filter(
        category__in=permited_categories, state=ArticleStates.PUBLISHED.value
    )

    return render(
        request,
        "article/home.html",
        {
            "permisos": permissions,
            "permited_categories": permited_categories,
            "not_permited_categories": not_permited_categories,
            "articles": articles,
        },
    )


def forbidden(request):
    """
    Vista que muestra la página de acceso prohibido.

    Args:
        request (HttpRequest): La solicitud HTTP.

    Returns:
        HttpResponse: Renderiza la plantilla 'article/forbidden.html'.
    """

    return render(request, "article/forbidden.html")


# =============================================================================
# Article
# =============================================================================


def article_create(request):
    """
    Vista que permite la creación de un artículo.

    Solo los usuarios autenticados y con el permiso `CREAR_ARTICULOS` pueden
    acceder a esta vista. Si no se cumplen las condiciones, se redirige al
    usuario a la página de login o a la página de acceso prohibido.

    Args:
        request (HttpRequest): La solicitud HTTP.

    Returns:
        HttpResponse: Renderiza la plantilla 'article/create_article.html' o redirige.
    """

    if not request.user.is_authenticated:
        return redirect("login")

    if not request.user.tiene_permisos([PermissionEnum.CREAR_ARTICULOS]):
        return redirect("forbidden")

    if request.method == "POST":
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.autor = request.user
            article.save()

            ArticleContent.objects.create(
                body=request.POST.get("body"), autor=request.user, article=article
            )

            return redirect("home")

    return render(request, "article/article_form.html", {"form": ArticleForm})


def article_update(request, pk):
    """
    Vista que permite la actualización de un artículo.

    Solo los usuarios autenticados y con el permiso `EDITAR_ARTICULOS` pueden
    acceder a esta vista. Si no se cumplen las condiciones, se redirige al
    usuario a la página de login o a la página de acceso prohibido.

    Args:
        request (HttpRequest): La solicitud HTTP.
        pk (int): El ID del artículo a actualizar.

    Returns:
        HttpResponse: Renderiza la plantilla 'article/update_article.html' o redirige.
    """

    if not request.user.is_authenticated:
        return redirect("login")

    if not request.user.tiene_permisos([PermissionEnum.EDITAR_ARTICULOS]):
        return redirect("forbidden")

    article = get_object_or_404(Article, pk=pk)

    if request.method == "POST":
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            article = form.save(commit=False)
            article.save()

            ArticleContent.objects.create(
                body=request.POST.get("body"), autor=request.user, article=article
            )

            return redirect("home")
    else:
        form = ArticleForm(instance=article)

        last_content = ArticleContent.objects.filter(article=article).last()
        if last_content:
            form.initial["body"] = last_content.body

    return render(request, "article/article_form.html", {"form": form})


def article_update_history(request, pk):
    """
    Vista que muestra el historial de versiones de un artículo.

    Solo los usuarios autenticados y con el permiso `VER_HISTORIAL_ARTICULOS`
    pueden acceder a esta vista. Si no se cumplen las condiciones, se redirige
    al usuario a la página de login o a la página de acceso prohibido.

    Args:
        request (HttpRequest): La solicitud HTTP.
        pk (int): El ID del artículo.

    Returns:
        HttpResponse: Renderiza la plantilla 'article/article_update_history.html' o redirige.
    """

    if not request.user.is_authenticated:
        return redirect("login")

    if not request.user.tiene_permisos([PermissionEnum.EDITAR_ARTICULOS]):
        return redirect("forbidden")

    if request.method == "POST":
        article_id = request.POST.get("article_id")
        article_content_id = request.POST.get("article_content_id")

        if not article_content_id or not article_id:
            return HttpResponse("No se ha encontrado el contenido", status=404)

        article_content = get_object_or_404(ArticleContent, pk=article_content_id)
        article = get_object_or_404(Article, pk=article_id)

        ArticleContent.objects.create(
            body=article_content.body, autor=request.user, article=article
        )

        return redirect("home")

    article = get_object_or_404(Article, pk=pk)
    article_contents_ref = ArticleContent.objects.filter(article=article)

    article_contents = [
        {
            "id": article_content.id,
            "autor": article_content.autor,
            "created_at": article_content.created_at,
            "body": mistune.html(article_content.body),
        }
        for article_content in article_contents_ref
    ]

    return render(
        request,
        "article/article_update_history.html",
        {"article": article, "article_contents": article_contents},
    )


def article_list(request):
    """
    Vista que muestra la lista de artículos.

    Solo los usuarios autenticados y con el permiso `VER_ARTICULOS` pueden
    acceder a esta vista. Si no se cumplen las condiciones, se redirige al
    usuario a la página de login o a la página de acceso prohibido.

    Args:
        request (HttpRequest): La solicitud HTTP.

    Returns:
        HttpResponse: Renderiza la plantilla 'article/article_list.html' o redirige.
    """

    if not request.user.is_authenticated:
        return redirect("login")

    if not request.user.tiene_permisos([PermissionEnum.VER_INICIO]):
        return redirect("forbidden")

    articles = Article.objects.all()
    can_create = request.user.tiene_permisos([PermissionEnum.CREAR_ARTICULOS])
    
    return render(
        request,
        "article/article_list.html",
        {
            "articles": articles,
            "can_create": can_create,  
        },
    )


def article_detail(request, pk):
    """
    Vista que muestra el detalle de un artículo.

    Solo los usuarios autenticados y con el permiso `VER_ARTICULOS` pueden
    acceder a esta vista. Si no se cumplen las condiciones, se redirige al
    usuario a la página de login o a la página de acceso prohibido.

    Args:
        request (HttpRequest): La solicitud HTTP.
        pk (int): El ID del artículo.

    Returns:
        HttpResponse: Renderiza la plantilla 'article/article_detail.html' o redirige.
    """

    if not request.user.is_authenticated:
        return redirect("login")

    if not request.user.tiene_permisos([PermissionEnum.VER_INICIO]):
        return redirect("forbidden")

    article = get_object_or_404(Article, pk=pk)
    article_content = ArticleContent.objects.filter(article=article).last()

    if not article_content:
        return HttpResponse("No hay contenido para este artículo", status=404)

    can_edit = request.user.tiene_permisos([PermissionEnum.EDITAR_ARTICULOS])
    can_publish = request.user.tiene_permisos([PermissionEnum.MODERAR_ARTICULOS])
    is_moderated_category = article.category.is_moderated

    article_render_content = mistune.html(article_content.body)

    return render(
        request,
        "article/article_detail.html",
        {
            "article": article,
            "article_render_content": article_render_content,
            "can_edit": can_edit,
            "can_publish": can_publish,
            "is_moderated_category": is_moderated_category,
        },
    )


def article_to_revision(request, pk):
    """
    Vista que cambia el estado de un artículo a Revisión.

    Args:
        request (HttpRequest): La solicitud HTTP.
        pk (int): El ID del artículo.
    """

    article = get_object_or_404(Article, pk=pk)

    if article.state != ArticleStates.DRAFT.value:
        return HttpResponseBadRequest(
            "El artículo debe estar en Borrador para pasar a Revisión"
        )

    article.change_state(ArticleStates.REVISION.value)
    return redirect("article-detail", pk=pk)


def article_to_published(request, pk):
    """
    Vista que cambia el estado de un artículo a Publicado.

    Args:
        request (HttpRequest): La solicitud HTTP.
        pk (int): El ID del artículo.
    """

    article = get_object_or_404(Article, pk=pk)

    can_publish = request.user.tiene_permisos([PermissionEnum.MODERAR_ARTICULOS])
    
    if not can_publish:
        return redirect("forbidden")

    if article.state != ArticleStates.REVISION.value:
        return HttpResponseBadRequest(
            "El artículo debe estar en revisión para publicarse"
        )

    article.change_state(ArticleStates.PUBLISHED.value)
    return redirect("article-detail", pk=pk)


def article_to_draft(request, pk):
    """
    Vista que cambia el estado de un artículo a Borrador.

    Args:
        request (HttpRequest): La solicitud HTTP.
        pk (int): El ID del artículo
    """

    article = get_object_or_404(Article, pk=pk)

    article.change_state(ArticleStates.DRAFT.value)
    return redirect("article-detail", pk=pk)


def article_to_inactive(request, pk):
    """
    Vista que cambia el estado de un artículo a Inactivo.

    Args:
        request (HttpRequest): La solicitud HTTP.
        pk (int): El ID del artículo
    """

    article = get_object_or_404(Article, pk=pk)

    article.change_state(ArticleStates.INACTIVE.value)
    return redirect("article-detail", pk=pk)


# =============================================================================
# Category views
# =============================================================================


def category_list(request):
    """
    Vista que muestra la lista de categorías.

    Solo los usuarios autenticados y con el permiso `MANEJAR_CATEGORIAS` pueden
    acceder a esta vista. Si no se cumplen las condiciones, se redirige al
    usuario a la página de login o a la página de acceso prohibido.

    Args:
        request (HttpRequest): La solicitud HTTP.

    Returns:
        HttpResponse: Renderiza la plantilla 'article/category_list.html' o redirige.
    """

    if not request.user.is_authenticated:
        return redirect("login")

    if not request.user.tiene_permisos([PermissionEnum.MANEJAR_CATEGORIAS]):
        return redirect("forbidden")

    categories = Category.objects.all()

    return render(request, "article/category_list.html", {"categories": categories})


def category_detail(request, pk):
    """
    Vista que muestra el detalle de una categoría específica.

    Solo los usuarios autenticados y con el permiso `MANEJAR_CATEGORIAS` pueden
    acceder a esta vista. Si no se cumplen las condiciones, se redirige al
    usuario a la página de login o a la página de acceso prohibido.

    Args:
        request (HttpRequest): La solicitud HTTP.
        pk (int): El ID de la categoría.

    Returns:
        HttpResponse: Renderiza la plantilla 'article/category_detail.html' o redirige.
    """

    if not request.user.is_authenticated:
        return redirect("login")

    if not request.user.tiene_permisos([PermissionEnum.MANEJAR_CATEGORIAS]):
        return redirect("forbidden")

    category = get_object_or_404(Category, pk=pk)
    return render(request, "article/category_detail.html", {"category": category})


def category_create(request):
    """
    Vista que permite la creación de una nueva categoría.

    Solo los usuarios autenticados y con el permiso `MANEJAR_CATEGORIAS` pueden
    acceder a esta vista. Si no se cumplen las condiciones, se redirige al
    usuario a la página de login o a la página de acceso prohibido.

    Args:
        request (HttpRequest): La solicitud HTTP.

    Returns:
        HttpResponse: Renderiza la plantilla 'article/category_form.html' o redirige.
    """

    if not request.user.is_authenticated:
        return redirect("login")

    if not request.user.tiene_permisos([PermissionEnum.MANEJAR_CATEGORIAS]):
        return redirect("forbidden")

    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("category-list")
    else:
        form = CategoryForm()

    return render(request, "article/category_form.html", {"form": form})


def category_update(request, pk):
    """
    Vista que permite actualizar una categoría existente.

    Solo los usuarios autenticados y con el permiso `MANEJAR_CATEGORIAS` pueden
    acceder a esta vista. Si no se cumplen las condiciones, se redirige al
    usuario a la página de login o a la página de acceso prohibido.

    Args:
        request (HttpRequest): La solicitud HTTP.
        pk (int): El ID de la categoría a actualizar.

    Returns:
        HttpResponse: Renderiza la plantilla 'article/category_form.html' o redirige.
    """

    if not request.user.is_authenticated:
        return redirect("login")

    if not request.user.tiene_permisos([PermissionEnum.MANEJAR_CATEGORIAS]):
        return redirect("forbidden")

    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect("category-list")
    else:
        form = CategoryForm(instance=category)

    return render(request, "article/category_form.html", {"form": form})


def category_delete(request, pk):
    """
    Vista que permite eliminar una categoría existente.

    Solo los usuarios autenticados y con el permiso `MANEJAR_CATEGORIAS` pueden
    acceder a esta vista. Si no se cumplen las condiciones, se redirige al
    usuario a la página de login o a la página de acceso prohibido.

    Args:
        request (HttpRequest): La solicitud HTTP.
        pk (int): El ID de la categoría a eliminar.

    Returns:
        HttpResponse: Renderiza la plantilla 'article/category_confirm_delete.html' o redirige.
    """

    if not request.user.is_authenticated:
        return redirect("login")

    if not request.user.tiene_permisos([PermissionEnum.MANEJAR_CATEGORIAS]):
        return redirect("forbidden")

    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        category.delete()
        return redirect("category-list")

    return render(
        request, "article/category_confirm_delete.html", {"category": category}
    )
