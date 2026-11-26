from decimal import Decimal
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from dashboard.models import Complaint
from delivery.models import Courier
from orders.models import Order
from restaurants.models import Restaurant


@staff_member_required(login_url="/admin/login/")
def ops_dashboard(request):
    today = timezone.localdate()

    # 1. KPI Calculations
    today_orders = Order.objects.filter(created_at__date=today)
    today_revenue = (
        today_orders.filter(
            payment_status__in=[Order.PaymentStatus.PAID, Order.PaymentStatus.UNPAID]
        ).aggregate(total=Sum("total_amount"))["total"]
        or Decimal("0.00")
    )
    today_order_count = today_orders.count()

    active_statuses = [
        Order.Status.PENDING,
        Order.Status.ACCEPTED,
        Order.Status.PREPARING,
        Order.Status.READY,
        Order.Status.OUT_FOR_DELIVERY,
    ]
    active_orders_count = Order.objects.filter(status__in=active_statuses).count()

    pending_restaurants_count = Restaurant.objects.filter(is_approved=False).count()
    open_complaints_count = Complaint.objects.filter(
        status__in=[Complaint.Status.OPEN, Complaint.Status.IN_PROGRESS]
    ).count()
    available_couriers_count = Courier.objects.filter(is_available=True).count()

    # 2. Actionable Queues
    pending_restaurants = Restaurant.objects.filter(is_approved=False).order_by("-created_at")[:10]
    unresolved_complaints = Complaint.objects.filter(
        status__in=[Complaint.Status.OPEN, Complaint.Status.IN_PROGRESS]
    ).select_related("order__customer__user", "order__restaurant").order_by("created_at")[:10]

    active_orders = (
        Order.objects.filter(status__in=active_statuses)
        .select_related("customer__user", "restaurant", "courier__user")
        .order_by("-created_at")[:15]
    )

    available_couriers = Courier.objects.filter(is_available=True).select_related("user")

    context = {
        "today_revenue": today_revenue,
        "today_order_count": today_order_count,
        "active_orders_count": active_orders_count,
        "pending_restaurants_count": pending_restaurants_count,
        "open_complaints_count": open_complaints_count,
        "available_couriers_count": available_couriers_count,
        "pending_restaurants": pending_restaurants,
        "unresolved_complaints": unresolved_complaints,
        "active_orders": active_orders,
        "available_couriers": available_couriers,
    }
    return render(request, "dashboard/ops_dashboard.html", context)


@require_POST
@staff_member_required(login_url="/admin/login/")
def approve_restaurant(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    action = request.POST.get("action", "approve")

    if action == "approve":
        restaurant.is_approved = True
        restaurant.save(update_fields=["is_approved"])
        messages.success(request, f"Restaurant '{restaurant.name}' has been approved and is now live.")
    elif action == "reject":
        restaurant.is_approved = False
        restaurant.is_active = False
        restaurant.save(update_fields=["is_approved", "is_active"])
        messages.warning(request, f"Restaurant '{restaurant.name}' application was rejected.")

    return redirect("dashboard:ops_dashboard")


@require_POST
@staff_member_required(login_url="/admin/login/")
def update_complaint(request, complaint_id):
    complaint = get_object_or_404(Complaint, pk=complaint_id)
    new_status = request.POST.get("status")
    admin_notes = request.POST.get("admin_notes", "").strip()

    if admin_notes:
        complaint.admin_notes = admin_notes

    if new_status in Complaint.Status.values:
        complaint.status = new_status
        if new_status == Complaint.Status.RESOLVED:
            complaint.resolved_at = timezone.now()
        complaint.save()
        messages.success(request, f"Complaint #{complaint.complaint_id} status updated to {complaint.get_status_display()}.")

    return redirect("dashboard:ops_dashboard")


@require_POST
@staff_member_required(login_url="/admin/login/")
def assign_courier(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    courier_id = request.POST.get("courier_id")

    if courier_id:
        courier = get_object_or_404(Courier, pk=courier_id)
        order.courier = courier
        order.save(update_fields=["courier"])
        messages.success(request, f"Courier {courier.user.get_full_name() or courier.user.username} assigned to Order #{order.order_id}.")
    else:
        order.courier = None
        order.save(update_fields=["courier"])
        messages.info(request, f"Courier unassigned from Order #{order.order_id}.")

    return redirect("dashboard:ops_dashboard")
