from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("ops/", views.ops_dashboard, name="ops_dashboard"),
    path("restaurants/<int:restaurant_id>/approve/", views.approve_restaurant, name="approve_restaurant"),
    path("complaints/<int:complaint_id>/update/", views.update_complaint, name="update_complaint"),
    path("orders/<int:order_id>/assign-courier/", views.assign_courier, name="assign_courier"),
]
