import mistune

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from roles.utils import PermissionEnum
from article.models import (
    Category,
    ArticleContent,
    Article,
    ArticleStates,
    CategoryType,
    ArticleVote,
)
from article.forms import *
from django.db.models import Avg


def home(request):
    """
    Vista que muestra la página principal del artículo.
    """

    categories = Category.objects.all()

    if not request.user.is_authenticated:
        permissions = []

        # Allow viewing of all categories but restrict access based on type
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

    # Fetch all articles for the home page
    articles = Article.objects.filter(state=ArticleStates.PUBLISHED.value)

    # Add average rating for each article
    for article in articles:
        ratings = ArticleVote.objects.filter(article=article)
        avg_rating = ratings.aggregate(Avg("rating"))["rating__avg"]

        # Check if avg_rating is None before rounding
        if avg_rating is not None:
            article.avg_rating = round(avg_rating, 1)
        else:
            article.avg_rating = None  # Or set it to 0 if you prefer

    authenticated = request.user.is_authenticated

    return render(
        request,
        "article/home.html",
        {
            "permisos": permissions,
            "permited_categories": permited_categories,
            "not_permited_categories": not_permited_categories,
            "articles": articles,
            "authenticated": authenticated,
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

    if not request.user.tiene_permisos(
        [PermissionEnum.EDITAR_ARTICULOS]
    ) and not request.user.tiene_permisos([PermissionEnum.EDITAR_ARTICULOS_BORRADOR]):
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
    article_contents_ref = ArticleContent.objects.filter(article=article).order_by('-created_at')

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

    can_create = request.user.tiene_permisos([PermissionEnum.CREAR_ARTICULOS])
    can_edit = request.user.tiene_permisos([PermissionEnum.EDITAR_ARTICULOS])
    can_publish = request.user.tiene_permisos([PermissionEnum.MODERAR_ARTICULOS])

    articles = []

    if can_publish or can_edit:
        articles = Article.objects.all()
    elif can_create:
        articles = Article.objects.filter(autor=request.user)

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
    Vista que muestra los detalles de un artículo.

    Si el usuario no está autenticado, se le permitirá ver el artículo solo si
    pertenece a una categoría gratuita. Para los usuarios autenticados, también
    se maneja la lógica de 'me gusta', 'no me gusta' y calificación.

    Args:
        request (HttpRequest): La solicitud HTTP.
        pk (int): El ID del artículo a mostrar.

    Returns:
        HttpResponse: Renderiza la plantilla 'article/article_detail.html'.
    """

    # Fetch the article and its content
    article = get_object_or_404(Article, pk=pk)
    article_content = ArticleContent.objects.filter(article=article).last()

    if not article_content:
        return HttpResponse("No content for this article", status=404)

    # Check if the article's category is "free"
    is_free = article.category.type == CategoryType.FREE.value
    authenticated = request.user.is_authenticated

    # Handle unauthenticated users (unknown users)
    if not authenticated:
        if is_free:
            # Unknown user can only view the article without interactions
            article.views_number += 1
            article.save()

            # Calculate the average rating for the article
            ratings = ArticleVote.objects.filter(article=article)
            avg_rating = ratings.aggregate(Avg("rating"))["rating__avg"]

            # Check if the average rating is None before rounding
            if avg_rating is not None:
                avg_rating = round(avg_rating, 1)

            # Convert article content body using mistune
            article_render_content = mistune.html(article_content.body)

            return render(
                request,
                "article/article_detail.html",
                {
                    "article": article,
                    "article_render_content": article_render_content,
                    "avg_rating": avg_rating,
                    # Unauthenticated users cannot edit, like, dislike, or publish
                    "can_edit_as_editor": False,
                    "can_edit_as_author": False,
                    "can_edit": False,
                    "can_publish": False,
                    "can_inactivate": False,
                    "is_moderated_category": article.category.is_moderated,
                    "user_vote": None,  # No vote for unauthenticated users
                    "authenticated": authenticated,
                },
            )
        else:
            # If the article is not free, redirect to login
            return redirect("login")

    # Else block for authenticated users
    else:
        # Ensure user has the right permissions
        if not request.user.tiene_permisos([PermissionEnum.VER_INICIO]):
            return redirect("forbidden")

        # Increment view count
        article.views_number += 1
        article.save()

        # Fetch the user's vote and rating for the article
        user_vote = ArticleVote.objects.filter(
            article=article, user=request.user
        ).first()

        # Handle like/dislike and rating submissions
        if request.method == "POST":
            if "rating" in request.POST:
                # Rating submission logic
                rating_value = int(request.POST.get("rating"))
                if user_vote:
                    user_vote.rating = rating_value
                    user_vote.save()
                else:
                    ArticleVote.objects.create(
                        user=request.user, article=article, rating=rating_value
                    )

            elif "like" in request.POST or "dislike" in request.POST:
                # Handle like/dislike submission
                if "like" in request.POST:
                    if user_vote and user_vote.vote != ArticleVote.LIKE:
                        if user_vote.vote == ArticleVote.DISLIKE:
                            article.dislikes_number -= 1
                        user_vote.vote = ArticleVote.LIKE
                        article.likes_number += 1
                        user_vote.save()
                    elif not user_vote:
                        ArticleVote.objects.create(
                            user=request.user, article=article, vote=ArticleVote.LIKE
                        )
                        article.likes_number += 1

                elif "dislike" in request.POST:
                    if user_vote and user_vote.vote != ArticleVote.DISLIKE:
                        if user_vote.vote == ArticleVote.LIKE:
                            article.likes_number -= 1
                        user_vote.vote = ArticleVote.DISLIKE
                        article.dislikes_number += 1
                        user_vote.save()
                    elif not user_vote:
                        ArticleVote.objects.create(
                            user=request.user, article=article, vote=ArticleVote.DISLIKE
                        )
                        article.dislikes_number += 1

                article.save()

        # Calculate the average rating for the article
        ratings = ArticleVote.objects.filter(article=article)
        avg_rating = ratings.aggregate(Avg("rating"))["rating__avg"]

        # Check if the average rating is None before rounding
        if avg_rating is not None:
            avg_rating = round(avg_rating, 1)

        # Check if the user is an admin
        is_admin = request.user.roles.filter(name="Administrador").exists()

        # Check if the user is the author of the article
        is_author = article.autor == request.user

        # Determine if the user can inactivate (either admin or author)
        can_inactivate = is_admin or is_author

        # Determine if the user can edit as an editor or author
        can_edit_as_editor = is_admin or request.user.tiene_permisos(
            [PermissionEnum.EDITAR_ARTICULOS]
        )
        can_edit_as_author = (
            is_author
            and request.user.tiene_permisos([PermissionEnum.EDITAR_ARTICULOS_BORRADOR])
        ) or is_admin

        # General edit permission (either editor or author)
        can_edit = can_edit_as_editor or can_edit_as_author

        # Can publish only if the user has permission to moderate articles
        can_publish = request.user.tiene_permisos([PermissionEnum.MODERAR_ARTICULOS])

        # Check if the category requires moderation
        is_moderated_category = article.category.is_moderated

        # Convert article content body using mistune
        article_render_content = mistune.html(article_content.body)

        return render(
            request,
            "article/article_detail.html",
            {
                "article": article,
                "article_render_content": article_render_content,
                "can_edit_as_editor": can_edit_as_editor,
                "can_edit_as_author": can_edit_as_author,
                "can_edit": can_edit,
                "can_publish": can_publish,
                "can_inactivate": can_inactivate,
                "is_moderated_category": is_moderated_category,
                "avg_rating": avg_rating,
                "user_vote": user_vote,  # Pass both vote and rating information to the template
                "authenticated": authenticated,
                "is_author": is_author,
                "is_admin": is_admin,
            },
        )


@login_required
def article_to_revision(request, pk):
    """
    Vista que cambia el estado de un artículo a Revisión.


    Args:
        request (HttpRequest): La solicitud HTTP.
        pk (int): El ID del artículo.
    """

    article = get_object_or_404(Article, pk=pk)

    is_admin = request.user.roles.filter(name="Administrador").exists()
    is_autor = request.user.tiene_permisos([PermissionEnum.CREAR_ARTICULOS])
    is_editor = request.user.tiene_permisos([PermissionEnum.EDITAR_ARTICULOS])
    is_publisher = request.user.tiene_permisos([PermissionEnum.MODERAR_ARTICULOS])

    # Solo el autor (cuando el estado es DRAFT) o el admin puede cambiar a REVISIÓN
    if (
        is_admin
        or (is_autor and article.state == ArticleStates.DRAFT.value)
        or ((is_editor or is_publisher) and article.state == ArticleStates.EDITED.value)
    ):
        article.change_state(ArticleStates.REVISION.value)
        return redirect("article-detail", pk=pk)

    return HttpResponseForbidden("No puedes editar este contenido")


@login_required
def article_to_published(request, pk):
    """
    Vista que cambia el estado de un artículo a Publicado.

    Args:
        request (HttpRequest): La solicitud HTTP.
        pk (int): El ID del artículo.
    """
    article = get_object_or_404(Article, pk=pk)

    is_admin = request.user.roles.filter(name="Administrador").exists()
    can_publish = is_admin or request.user.tiene_permisos([PermissionEnum.MODERAR_ARTICULOS])
    is_moderated = article.category.is_moderated
    is_author = article.autor == request.user

    # Solo el publicador o el admin puede cambiar a PUBLICADO
    if is_moderated:
        if can_publish and article.state == ArticleStates.EDITED.value:
            article.change_state(ArticleStates.PUBLISHED.value)
            return redirect("article-detail", pk=pk)
    else:
        if is_author or is_admin or can_publish:
            article.change_state(ArticleStates.PUBLISHED.value)
            return redirect("article-detail", pk=pk)
        
    return HttpResponseForbidden("No puedes editar este contenido")



@login_required
def article_to_edited(request, pk):
    """
    Vista que cambia el estado de un artículo a Editado.

    Args:
        request (HttpRequest): La solicitud HTTP.
        pk (int): El ID del artículo.
    """
    article = get_object_or_404(Article, pk=pk)

    is_admin = request.user.roles.filter(name="Administrador").exists()
    is_editor = is_admin or request.user.tiene_permisos(
        [PermissionEnum.EDITAR_ARTICULOS]
    )

    # Solo el editor o el admin pueden cambiar a EDITADO y el estado actual debe ser REVISIÓN
    if is_editor and article.state == ArticleStates.REVISION.value:
        article.change_state(ArticleStates.EDITED.value)
        return redirect("article-detail", pk=pk)

    return HttpResponseForbidden("No puedes editar este contenido")


@login_required
def article_to_draft(request, pk):
    """
    Vista que cambia el estado de un artículo a Borrador.

    Args:
        request (HttpRequest): La solicitud HTTP.
        pk (int): El ID del artículo.
    """
    article = get_object_or_404(Article, pk=pk)

    is_admin = request.user.roles.filter(name="Administrador").exists()
    is_editor = is_admin or request.user.tiene_permisos(
        [PermissionEnum.EDITAR_ARTICULOS]
    )

    # Solo el autor (cuando el estado es REVISION) o el admin puede cambiar a DRAFT
    if is_admin or (is_editor and article.state == ArticleStates.REVISION.value):
        article.change_state(ArticleStates.DRAFT.value)
        return redirect("article-detail", pk=pk)

    return HttpResponseForbidden("No puedes editar este contenido")


@login_required
def article_to_inactive(request, pk):
    """
    Vista que cambia el estado de un artículo a Inactivo.

    Args:
        request (HttpRequest): La solicitud HTTP.
        pk (int): El ID del artículo.
    """
    article = get_object_or_404(Article, pk=pk)

    is_admin = request.user.roles.filter(name="Administrador").exists()
    is_autor = request.user.tiene_permisos([PermissionEnum.CREAR_ARTICULOS])

    # Solo el autor o el admin puede cambiar a INACTIVO
    if is_admin or is_autor:
        article.change_state(ArticleStates.INACTIVE.value)
        return redirect("article-detail", pk=pk)

    return HttpResponseForbidden("No puedes editar este contenido")


# =============================================================================
# Category views
# =============================================================================


# def category_list(request):
#     """
#     Vista que muestra la lista de categorías.

#     Solo los usuarios autenticados y con el permiso `MANEJAR_CATEGORIAS` pueden
#     acceder a esta vista. Si no se cumplen las condiciones, se redirige al
#     usuario a la página de login o a la página de acceso prohibido.

#     Args:
#         request (HttpRequest): La solicitud HTTP.

#     Returns:
#         HttpResponse: Renderiza la plantilla 'article/category_list.html' o redirige.
#     """

#     if not request.user.is_authenticated:
#         return redirect("login")

#     if not request.user.tiene_permisos([PermissionEnum.MANEJAR_CATEGORIAS]):
#         return redirect("forbidden")

#     categories = Category.objects.all()

#     return render(request, "article/category_list.html", {"categories": categories})

def category_list(request):
    """
    Vista que muestra la lista de categorías y permite buscar, filtrar y ordenar resultados.
    
    Muestra todas las categorías de manera predeterminada y actualiza los resultados según 
    la entrada del formulario de búsqueda.

    Args:
        request (HttpRequest): La solicitud HTTP.

    Returns:
        HttpResponse: Renderiza la plantilla 'article/category_list.html' o redirige.
    """
    form = CategorySearchForm(request.GET or None)
    categories = Category.objects.all()

    if form.is_valid():
        search_term = form.cleaned_data.get('search_term')
        order_by = form.cleaned_data.get('order_by', 'name')
        filter_type = form.cleaned_data.get('filter_type', 'all')

        print("Valor de order_by:", order_by)

        # Filtrar por título que contenga el término de búsqueda
        if search_term:
            categories = categories.filter(name__icontains=search_term)

        # Filtrar por tipo de categoría
        if filter_type != 'all':
            categories = categories.filter(type=filter_type)

        # Ordenar los resultados
        categories = categories.order_by(order_by)

        print("Lista de categorías ordenadas:")
        for category in categories:
            print(category.name)

    return render(request, 'article/category_list.html', {'form': form, 'categories': categories})


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

# =============================================================================
# Calificaciones views
# =============================================================================

@login_required
def like_article(request, pk):
    """
    Vista que permite que un usuario marque como 'me gusta' un artículo.

    Si el usuario ya ha marcado el artículo como 'no me gusta', se revierte
    esa acción antes de marcarlo como 'me gusta'. Si es la primera vez que
    marca el artículo, simplemente se incrementa el contador de 'me gusta'.

    Args:
        request (HttpRequest): La solicitud HTTP.
        pk (int): El ID del artículo al que se está aplicando el 'me gusta'.

    Returns:
        HttpResponse: Redirige a la vista de detalle del artículo.
    """
    article = get_object_or_404(Article, pk=pk)
    # Get or create the vote, ensuring that 'vote' is not null
    vote, created = ArticleVote.objects.get_or_create(
        user=request.user, article=article, defaults={"vote": ArticleVote.LIKE}
    )

    if not created and vote.vote != ArticleVote.LIKE:
        # If user previously disliked, undo that dislike
        if vote.vote == ArticleVote.DISLIKE:
            article.dislikes_number -= 1
        # Set the vote to like
        vote.vote = ArticleVote.LIKE
        article.likes_number += 1
        vote.save()

    elif created:
        # If this is the first time the user liked the article
        article.likes_number += 1

    article.save()
    return redirect("article-detail", pk=pk)


@login_required
def dislike_article(request, pk):
    """
    Vista que permite que un usuario marque como 'no me gusta' un artículo.

    Si el usuario ya ha marcado el artículo como 'me gusta', se revierte
    esa acción antes de marcarlo como 'no me gusta'. Si es la primera vez que
    marca el artículo, simplemente se incrementa el contador de 'no me gusta'.

    Args:
        request (HttpRequest): La solicitud HTTP.
        pk (int): El ID del artículo al que se está aplicando el 'no me gusta'.

    Returns:
        HttpResponse: Redirige a la vista de detalle del artículo.
    """
    article = get_object_or_404(Article, pk=pk)
    # Get or create the vote, ensuring that 'vote' is not null
    vote, created = ArticleVote.objects.get_or_create(
        user=request.user, article=article, defaults={"vote": ArticleVote.DISLIKE}
    )

    if not created and vote.vote != ArticleVote.DISLIKE:
        # If user previously liked, undo that like
        if vote.vote == ArticleVote.LIKE:
            article.likes_number -= 1
        # Set the vote to dislike
        vote.vote = ArticleVote.DISLIKE
        article.dislikes_number += 1
        vote.save()

    elif created:
        # If this is the first time the user disliked the article
        article.dislikes_number += 1

    article.save()
    return redirect("article-detail", pk=pk)
