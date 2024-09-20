from django.urls import path
from kanban import views

urlpatterns = [
    path("", views.kanban_view, name="kanban"),
]
