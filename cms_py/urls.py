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

import article.views as article
import user.views as user

from django.conf.urls.static import static
from django.urls import path, include
from django.conf import settings
from article.custom_mdeditor_views import CustomUploadView

urlpatterns = [
    path(
        "toggle_user_status/<int:user_id>/",
        user.toggle_user_status,
        name="toggle-user-status",
    ),
    path("forbidden", article.forbidden, name="forbidden"),
    path("", article.home, name="home"),
    # Authentication
    path("login/", user.login_view, name="login"),
    path("register/", user.register, name="register"),
    path("logout/", user.logout_view, name="logout"),
    path("profile/edit/", user.edit_profile, name="edit_profile"),
    path(r"article/", include("article.urls_articles")),
    path(r"categories/", include("article.urls_categories")),
    path(r"roles/", include("roles.urls")),
    path(r"kanban/", include("kanban.urls")),
    path(r"users/", include("user.urls")),
    # Mdeditor url config
    path("mdeditor/uploads/", CustomUploadView.as_view(), name="mdeditor_upload"),
    path("mdeditor/", include("mdeditor.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
