from django.urls import path
from kanban import views

urlpatterns = [
    path("", views.kanban_view, name="kanban"),
    path("send_message/", views.kanban_send_message, name="kanban-send-message"),
]
