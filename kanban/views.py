from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from article.models import Article, ArticleStates
from roles.utils import PermissionEnum


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
    if not is_editor or not is_admin or not is_publisher:
        draft_articles = draft_articles.filter(autor=request.user)
        revision_articles = revision_articles.filter(autor=request.user)
        edited_articles = edited_articles.filter(autor=request.user)
        published_articles = published_articles.filter(autor=request.user)
        inactive_articles = inactive_articles.filter(autor=request.user)

    print(
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
        }
    )

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
