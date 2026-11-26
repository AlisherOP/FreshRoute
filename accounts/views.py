from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse

from customers.models import Customer
from .forms import SignUpForm


def _get_role_redirect_url(user):
    if user.is_staff or user.is_superuser:
        return "/admin/"
    role = getattr(user, "role", "")
    if role == "OWNER":
        return "/restaurants/"
    if role == "COURIER":
        return "/delivery/"
    return reverse("customers:home")


class RoleLoginView(LoginView):
    template_name = "accounts/login.html"

    def get_success_url(self):
        return _get_role_redirect_url(self.request.user)


def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            if user.role == "CUSTOMER":
                Customer.objects.get_or_create(
                    user=user, defaults={"phone": ""})
            login(request, user)
            return redirect(_get_role_redirect_url(user))
    else:
        form = SignUpForm()
    return render(request, "accounts/signup.html", {"form": form})
