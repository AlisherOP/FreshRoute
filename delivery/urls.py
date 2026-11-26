from django.urls import path

from . import views

app_name = "delivery"

urlpatterns = [
    path("", views.courier_dashboard, name="courier_dashboard"),
]
