from django.urls import path
from article import views

urlpatterns = [
    path("", views.category_list, name="category-list"),
    path("<int:pk>/", views.category_detail, name="category-detail"),
    path("create/", views.category_create, name="category-create"),
    path(
        "<int:pk>/update/",
        views.category_update,
        name="category-update",
    ),
    path(
        "<int:pk>/delete/",
        views.category_delete,
        name="category-delete",
    )
]
