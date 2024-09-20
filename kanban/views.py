from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from article.models import Article, ArticleStates


@login_required
def kanban_view(request):
    draft_articles = Article.objects.filter(state=ArticleStates.DRAFT.value)
    revision_articles = Article.objects.filter(state=ArticleStates.REVISION.value)
    published_articles = Article.objects.filter(state=ArticleStates.PUBLISHED.value)
    inactive_articles = Article.objects.filter(state=ArticleStates.INACTIVE.value)

    return render(request, "kanban/kanban.html", {
        "draft_articles": draft_articles,
        "revision_articles": revision_articles,
        "published_articles": published_articles,
        "inactive_articles": inactive_articles,
    })
