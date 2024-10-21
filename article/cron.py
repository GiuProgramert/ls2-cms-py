from article.models import ArticlesToPublish, ArticleStates
from django.utils import timezone


def publish_schedule_articles():
    """
    Publica los articulos que estan en estado de programados.
    """
    print("Iniciando publicación de articulos programados")

    articles_to_publish = ArticlesToPublish.objects.filter(
        to_publish_at__lte=timezone.now(), published=False
    )

    for article_to_publish in articles_to_publish:
        print(f"Publicando articulo {article_to_publish.article.title}")
        print(
            f"Fecha de publicación: {article_to_publish.to_publish_at}, Fecha actual: {timezone.now()}"
        )
        article_to_publish.article.change_state(ArticleStates.PUBLISHED.value)
        article_to_publish.published = True
        article_to_publish.save()
        print(f"Articulo {article_to_publish.article.title} publicado")

    print("Finalizando publicación de articulos programados")
