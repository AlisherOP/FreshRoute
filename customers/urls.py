from django.urls import path
from . import views

app_name = "customers"

urlpatterns = [
    path("", views.profile_and_addresses, name="home"),
]
