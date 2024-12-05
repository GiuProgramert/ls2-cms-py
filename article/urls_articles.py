from django.urls import path
from article import views

urlpatterns = [
    path("", views.article_list, name="article-list"),
    path("create/", views.article_create, name="article-create"),
    path("<int:pk>/update/", views.article_update, name="article-update"),
    path(
        "<int:pk>/update/history/",
        views.article_update_history,
        name="article-update-history",
    ),
    path("<int:pk>/detail/", views.article_detail, name="article-detail"),
    path(
        "<int:pk>/update/state/revision/",
        views.article_to_revision,
        name="article-to-revision",
    ),
    path(
        "<int:pk>/update/state/published/",
        views.article_to_published,
        name="article-to-published",
    ),
    path(
        "<int:pk>/update/state/published/schedule/",
        views.article_to_publish_schedule,
        name="article-to-published-schedule",
    ),
    path(
        "<int:pk>/update/state/draft/", views.article_to_draft, name="article-to-draft"
    ),
    path(
        "<int:pk>/update/state/inactive/",
        views.article_to_inactive,
        name="article-to-inactive",
    ),
    path(
        "<int:pk>/update/state/edited/",
        views.article_to_edited,
        name="article-to-edited",
    ),
    path("<int:pk>/like/", views.like_article, name="like-article"),
    path("<int:pk>/dislike/", views.dislike_article, name="dislike-article"),
    path("sold-categories/", views.sold_categories, name="sold-categories"),
    path("likes-dislikes-chart/", views.article_stats, name="article-stats"),
    path(
        "sold-categories-suscriptor/",
        views.sold_categories_suscriptor,
        name="sold-categories-suscriptor",
    ),
    path(
        "sold-categories/download/",
        views.download_sold_categories,
        name="download-sold-categories",
    ),
    path(
        "sold-categories-suscriptor/download/",
        views.download_sold_categories_suscriptor,
        name="download-sold-categories-suscriptor",
    ),

     path("manage-featured-articles/", views.manage_featured_articles, name="manage-featured-articles"),
]
