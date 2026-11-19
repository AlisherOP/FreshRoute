from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path(
        "restaurants/<int:restaurant_id>/orders/",
        views.incoming_orders,
        name="incoming_orders",
    ),
    path(
        "restaurants/<int:restaurant_id>/orders/<int:order_id>/status/",
        views.change_order_status,
        name="change_order_status",
    ),
]
