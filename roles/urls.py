from django.urls import path
from roles import views

urlpatterns = [
    path("", views.role_list, name="role-list"),
    path("<int:pk>/detail", views.role_detail, name="role-detail"),
    path("create/", views.role_create, name="role-create"),
    path("<int:pk>/update/", views.role_update, name="role-update"),
    path("<int:pk>/delete/", views.role_delete, name="role-delete"),
]
