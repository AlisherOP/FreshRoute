from django.urls import path

from . import views

app_name = "restaurants"

urlpatterns = [
    path("dashboard/", views.owner_dashboard, name="owner_dashboard"),
    path("<int:restaurant_id>/menu/", views.menu_list, name="menu_list"),
    path("<int:restaurant_id>/menu/add/", views.product_add, name="product_add"),
    path(
        "<int:restaurant_id>/opening-hours/",
        views.opening_hours_edit,
        name="opening_hours",
    ),
    path(
        "<int:restaurant_id>/menu/<int:product_id>/edit/",
        views.product_edit,
        name="product_edit",
    ),
    path(
        "<int:restaurant_id>/menu/<int:product_id>/availability/",
        views.product_toggle_availability,
        name="product_toggle_availability",
    ),
]
