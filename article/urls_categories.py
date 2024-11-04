from django.urls import path
from article import views

urlpatterns = [
    path("", views.category_list, name="category-list"),
    path("<int:pk>/", views.category_detail, name="category-detail"),
    path(
        "<int:pk>/toggle-favorite/",
        views.toggle_favorite_category,
        name="toggle-favorite-category",
    ),
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
    ),
    path(
        "<int:pk>/checkout/", views.checkout_page, name="checkout_page"
    ),  # Página de checkout
    path(
        "crear-checkout-session/<int:pk>/",
        views.stripe_checkout,
        name="stripe_checkout",
    ),
    path("<int:pk>/success/", views.payment_success, name="payment_success"),
    path("<int:pk>/cancel/", views.payment_cancel, name="payment_cancel"),
    path("<int:pk>/cancel/", views.payment_cancel, name="payment_cancel"),
    path("<int:pk>/exists/", views.category_exists, name="category_exists"),
]
