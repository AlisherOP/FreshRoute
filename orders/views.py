import logging

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

from restaurants.decorators import owner_required
from restaurants.models import Restaurant

from .models import Order
from .notifications import send_order_status_email


logger = logging.getLogger(__name__)

OWNER_STATUS_ACTIONS = {
    Order.Status.PENDING: (
        (Order.Status.ACCEPTED, "Accept order"),
        (Order.Status.CANCELLED, "Cancel order"),
    ),
    Order.Status.ACCEPTED: (
        (Order.Status.PREPARING, "Start preparing"),
        (Order.Status.CANCELLED, "Cancel order"),
    ),
    Order.Status.PREPARING: (
        (Order.Status.READY, "Mark ready"),
    ),
}


@owner_required
def incoming_orders(request, restaurant_id):
    restaurant = get_object_or_404(
        Restaurant,
        pk=restaurant_id,
        owner=request.user,
    )
    orders = (
        Order.objects.filter(restaurant=restaurant)
        .exclude(status__in=[Order.Status.DELIVERED, Order.Status.CANCELLED])
        .select_related("customer__user")
        .prefetch_related("items__product")
        .order_by("-created_at")
    )
    orders = list(orders)
    for order in orders:
        order.owner_status_actions = OWNER_STATUS_ACTIONS.get(order.status, ())

    template_name = "orders/_incoming_order_list.html"
    if request.headers.get("HX-Request") != "true":
        template_name = "orders/incoming_orders.html"

    return render(
        request,
        template_name,
        {"restaurant": restaurant, "orders": orders},
    )


@owner_required
@require_POST
def change_order_status(request, restaurant_id, order_id):
    restaurant = get_object_or_404(
        Restaurant,
        pk=restaurant_id,
        owner=request.user,
    )
    order = get_object_or_404(
        Order,
        pk=order_id,
        restaurant=restaurant,
    )
    requested_status = request.POST.get("status", "")
    allowed_statuses = dict(OWNER_STATUS_ACTIONS.get(order.status, ()))

    if requested_status not in allowed_statuses:
        messages.error(request, "That status change is not allowed for this order.")
        return redirect("orders:incoming_orders", restaurant_id=restaurant.pk)

    try:
        order.set_status(requested_status)
    except ValidationError as error:
        messages.error(request, error.message)
        return redirect("orders:incoming_orders", restaurant_id=restaurant.pk)

    try:
        email_sent = send_order_status_email(order)
    except Exception:
        logger.exception("Could not send status email for order %s", order.pk)
        email_sent = False

    messages.success(
        request,
        f"Order #{order.pk} updated to {order.get_status_display()}.",
    )
    if not email_sent:
        messages.warning(
            request,
            "The order was updated, but an email could not be sent to the customer.",
        )
    return redirect("orders:incoming_orders", restaurant_id=restaurant.pk)
