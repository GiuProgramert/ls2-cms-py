"""
URL configuration for cmd_py project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

import article.views
import user.views
import roles.views

from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "toggle_user_status/<int:user_id>/",
        user.views.toggle_user_status,
        name="toggle-user-status",
    ),
    path("article/<int:pk>/like/", article.views.like_article, name="like-article"),
    path(
        "article/<int:pk>/dislike/",
        article.views.dislike_article,
        name="dislike-article",
    ),
    path("forbidden", article.views.forbidden, name="forbidden"),
    path("", article.views.home, name="home"),
    path("login/", user.views.login_view, name="login"),
    path("register/", user.views.register, name="register"),
    path("logout/", user.views.logout_view, name="logout"),
    # Article
    path("article/", article.views.article_list, name="article-list"),
    path("article/create", article.views.article_create, name="article-create"),
    path(
        "article/<int:pk>/update", article.views.article_update, name="article-update"
    ),
    path(
        "article/<int:pk>/update/history",
        article.views.article_update_history,
        name="article-update-history",
    ),
    path(
        "article/<int:pk>/detail", article.views.article_detail, name="article-detail"
    ),
    path(
        "article/<int:pk>/update/state/revision/",
        article.views.article_to_revision,
        name="article-to-revision",
    ),
    path(
        "article/<int:pk>/update/state/published/",
        article.views.article_to_published,
        name="article-to-published",
    ),
    path(
        "article/<int:pk>/update/state/draft/",
        article.views.article_to_draft,
        name="article-to-draft",
    ),
    path(
        "article/<int:pk>/update/state/inactive/",
        article.views.article_to_inactive,
        name="article-to-inactive",
    ),
    path("profile/edit/", user.views.edit_profile, name="edit_profile"),
    # Categories
    path("categories/", article.views.category_list, name="category-list"),
    path("categories/<int:pk>/", article.views.category_detail, name="category-detail"),
    path("categories/create/", article.views.category_create, name="category-create"),
    path(
        "categories/<int:pk>/update/",
        article.views.category_update,
        name="category-update",
    ),
    path(
        "categories/<int:pk>/delete/",
        article.views.category_delete,
        name="category-delete",
    ),
    # User
    path("users/", user.views.UserListView.as_view(), name="user-list"),
    path(
        "users/<int:pk>/asignar",
        roles.views.RoleAssignmentView.as_view(),
        name="assign_roles",
    ),
    # Roles
    path("roles/", roles.views.role_list, name="role-list"),
    path("roles/<int:pk>/detail", roles.views.role_detail, name="role-detail"),
    path("roles/create/", roles.views.role_create, name="role-create"),
    path("roles/<int:pk>/update/", roles.views.role_update, name="role-update"),
    path("roles/<int:pk>/delete/", roles.views.role_delete, name="role-delete"),
    path(r"mdeditor/", include("mdeditor.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
