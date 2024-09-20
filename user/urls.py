from django.urls import path
from user import views
from roles import views as roles_views

urlpatterns = [
    path("users/", views.UserListView.as_view(), name="user-list"),
    path(
        "users/<int:pk>/asignar",
        roles_views.RoleAssignmentView.as_view(),
        name="assign_roles",
    ),
]
