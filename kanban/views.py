from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseNotAllowed, HttpResponse
from django.contrib.auth.decorators import login_required
from article.models import Article, ArticleStates
from roles.utils import PermissionEnum
from notification.utils import send_email


@login_required
def kanban_view(request):
    draft_articles = Article.objects.filter(state=ArticleStates.DRAFT.value)
    revision_articles = Article.objects.filter(state=ArticleStates.REVISION.value)
    edited_articles = Article.objects.filter(state=ArticleStates.EDITED.value)
    published_articles = Article.objects.filter(state=ArticleStates.PUBLISHED.value)
    inactive_articles = Article.objects.filter(state=ArticleStates.INACTIVE.value)

    # Check if the user is an admin
    is_admin = request.user.roles.filter(name="Administrador").exists()

    # Check if the user is an editor
    is_editor = is_admin or request.user.tiene_permisos(
        [PermissionEnum.EDITAR_ARTICULOS]
    )

    is_publisher = is_admin or request.user.tiene_permisos(
        [PermissionEnum.MODERAR_ARTICULOS]
    )

    is_autor = request.user.tiene_permisos([PermissionEnum.CREAR_ARTICULOS])

    # Autors can only see their own articles
    if is_autor and not is_admin and not is_editor and not is_publisher:
        draft_articles = draft_articles.filter(autor=request.user)
        revision_articles = revision_articles.filter(autor=request.user)
        edited_articles = edited_articles.filter(autor=request.user)
        published_articles = published_articles.filter(autor=request.user)
        inactive_articles = inactive_articles.filter(autor=request.user)

    return render(
        request,
        "kanban/kanban.html",
        {
            "draft_articles": draft_articles,
            "revision_articles": revision_articles,
            "edited_articles": edited_articles,
            "published_articles": published_articles,
            "inactive_articles": inactive_articles,
            "is_admin": is_admin,
            "is_editor": is_editor,
            "is_publisher": is_publisher,
            "is_autor": is_autor,
            "ArticleStates": ArticleStates,
        },
    )


@login_required
def kanban_send_message(request):
    """
    Función que envía un mensaje a un usuario.

    Args:
        request (HttpRequest): La petición HTTP.

    Returns:
        HttpResponse: La respuesta HTTP.
    """
    if request.method == "POST":
        is_admin = request.user.roles.filter(name="Administrador").exists()

        is_editor = is_admin or request.user.tiene_permisos(
            [PermissionEnum.EDITAR_ARTICULOS]
        )

        if not is_editor and not is_admin:
            return HttpResponse(status=403)

        articleId = request.POST.get("articleId")
        message = request.POST.get("message")

        article = get_object_or_404(Article, pk=articleId)

        try:
            send_email(
                to=request.user.email,
                subject="CMS PY: Mensaje al modificar el estado del articulo",
                html=f"""
                    <h3>Hola, {article.autor.username}</h3>
                    <p>
                        {request.user.username} ha enviado un mensaje al modificar el estado del articulo <strong>{article.title}</strong>
                    </p>
                    <p>
                        {message}
                    </p>
                """,
            )
        except Exception:
            return HttpResponse(status=500)

        return HttpResponse(status=204)

    return HttpResponseNotAllowed(["POST"])
