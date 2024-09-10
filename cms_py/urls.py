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
    path("forbidden", article.views.forbidden, name="forbidden"),
    path("", article.views.home, name="home"),
    path("login/", user.views.login_view, name="login"),
    path("register/", user.views.register, name="register"),
    path("logout/", user.views.logout_view, name="logout"),
    path("article/", article.views.article_list, name="article-list"),
    path("article/create", article.views.article_create, name="article-create"),
    path(
        "article/<int:pk>/update", article.views.article_update, name="article-update"
    ),
    path("article/<int:pk>/update/history", article.views.article_update_history, name="article-update-history"),
    path("article/<int:pk>/detail", article.views.article_detail, name="article-detail"),
    path("profile/edit/", user.views.edit_profile, name="edit_profile"),
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
    path("roles/", user.views.UserListView.as_view(), name="user-list"),
    path(
        "roles/<int:pk>/asignar",
        roles.views.RoleAssignmentView.as_view(),
        name="assign_roles",
    ),
    path("users/", user.views.UserListView.as_view(), name="user-list"),

    path(r"mdeditor/", include("mdeditor.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
