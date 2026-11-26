from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render

from .models import Courier


@login_required
def courier_dashboard(request):
    if getattr(request.user, "role", None) != "COURIER":
        return HttpResponseForbidden("Courier access required.")

    courier, _ = Courier.objects.get_or_create(
        user=request.user,
        defaults={"phone": ""},
    )
    orders = (
        courier.deliveries.exclude(status__in=["DELIVERED", "CANCELLED"])
        .select_related("restaurant", "customer__user")
        .prefetch_related("items__product")
        .order_by("-created_at")
    )
    return render(
        request,
        "delivery/courier_dashboard.html",
        {"courier": courier, "orders": orders},
    )
