from django.shortcuts import render
from django.utils import timezone

from delivery.models import DeliveryZone
from orders.models import Coupon, Order
from restaurants.models import FoodProduct, Restaurant


def home(request):
    # Approved and active restaurants
    restaurants = (
        Restaurant.objects.filter(is_approved=True, is_active=True)
        .prefetch_related("products", "categories", "opening_hours")
        .order_by("name")
    )

    # Active delivery zones
    zones = DeliveryZone.objects.filter(is_active=True).order_by("fee")

    # Active promotional coupons
    coupons = Coupon.objects.filter(
        is_active=True,
        valid_until__gte=timezone.now(),
    ).select_related("restaurant")[:4]

    # Popular/featured food items
    featured_products = (
        FoodProduct.objects.filter(
            is_available=True,
            is_archived=False,
            restaurant__is_approved=True,
            restaurant__is_active=True,
        )
        .select_related("restaurant", "category")[:6]
    )

    # Operational metrics for display
    total_restaurants = Restaurant.objects.filter(is_approved=True, is_active=True).count()
    total_orders = Order.objects.count()
    pending_merchants = Restaurant.objects.filter(is_approved=False).count()

    # If the user is an owner, find their first restaurant for quick kitchen access
    owner_restaurant = None
    if request.user.is_authenticated and getattr(request.user, "role", "") == "OWNER":
        owner_restaurant = Restaurant.objects.filter(owner=request.user).first()
    elif not request.user.is_authenticated:
        # For demo purposes, pick the first restaurant so visitors can test the KDS link
        owner_restaurant = Restaurant.objects.filter(is_approved=True).first()

    context = {
        "restaurants": restaurants,
        "zones": zones,
        "coupons": coupons,
        "featured_products": featured_products,
        "total_restaurants": total_restaurants,
        "total_orders": total_orders,
        "pending_merchants": pending_merchants,
        "owner_restaurant": owner_restaurant,
    }
    return render(request, "home.html", context)
