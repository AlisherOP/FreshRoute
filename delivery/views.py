from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render

from .models import Courier


@login_required
def courier_dashboard(request):
    is_admin = request.user.is_staff or request.user.is_superuser
    if getattr(request.user, "role", None) != "COURIER" and not is_admin:
        return HttpResponseForbidden("Courier access required.")

    all_couriers = None
    target_courier_id = request.GET.get("courier_id")

    if is_admin:
        all_couriers = Courier.objects.select_related("user").order_by("user__username")
        if target_courier_id:
            courier = get_object_or_404(Courier, pk=target_courier_id)
        else:
            courier = all_couriers.first()
            if not courier:
                courier, _ = Courier.objects.get_or_create(
                    user=request.user,
                    defaults={"phone": ""},
                )
    else:
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
        {
            "courier": courier,
            "orders": orders,
            "is_admin": is_admin,
            "all_couriers": all_couriers,
        },
    )
