from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .decorators import owner_required
from .forms import FoodProductForm, OpeningHoursForm
from .models import FoodProduct, OpeningHour, Restaurant


def owned_restaurant_or_404(request, restaurant_id):
    return get_object_or_404(
        Restaurant,
        pk=restaurant_id,
        owner=request.user,
    )


@owner_required
def owner_dashboard(request):
    restaurants = (
        Restaurant.objects.filter(owner=request.user)
        .prefetch_related("opening_hours")
        .order_by("name")
    )
    return render(
        request,
        "restaurants/owner_dashboard.html",
        {"restaurants": restaurants},
    )


@owner_required
def menu_list(request, restaurant_id):
    restaurant = owned_restaurant_or_404(request, restaurant_id)
    products = (
        restaurant.products.filter(is_archived=False)
        .select_related("category")
        .order_by("name")
    )
    return render(
        request,
        "restaurants/menu_list.html",
        {"restaurant": restaurant, "products": products},
    )


@owner_required
def product_add(request, restaurant_id):
    restaurant = owned_restaurant_or_404(request, restaurant_id)
    if request.method == "POST":
        form = FoodProductForm(
            request.POST,
            request.FILES,
            restaurant=restaurant,
        )
        if form.is_valid():
            product = form.save(commit=False)
            product.restaurant = restaurant
            product.save()
            messages.success(request, "Menu item added.")
            return redirect("restaurants:menu_list", restaurant_id=restaurant.pk)
    else:
        form = FoodProductForm(restaurant=restaurant)

    return render(
        request,
        "restaurants/product_form.html",
        {"form": form, "restaurant": restaurant, "page_title": "Add menu item"},
    )


@owner_required
def product_edit(request, restaurant_id, product_id):
    restaurant = owned_restaurant_or_404(request, restaurant_id)
    product = get_object_or_404(
        FoodProduct,
        pk=product_id,
        restaurant=restaurant,
        is_archived=False,
    )
    if request.method == "POST":
        form = FoodProductForm(
            request.POST,
            request.FILES,
            instance=product,
            restaurant=restaurant,
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Menu item updated.")
            return redirect("restaurants:menu_list", restaurant_id=restaurant.pk)
    else:
        form = FoodProductForm(instance=product, restaurant=restaurant)

    return render(
        request,
        "restaurants/product_form.html",
        {"form": form, "restaurant": restaurant, "page_title": "Edit menu item"},
    )


@owner_required
@require_POST
def product_toggle_availability(request, restaurant_id, product_id):
    restaurant = owned_restaurant_or_404(request, restaurant_id)
    product = get_object_or_404(
        FoodProduct,
        pk=product_id,
        restaurant=restaurant,
        is_archived=False,
    )
    product.is_available = not product.is_available
    product.save(update_fields=["is_available"])
    messages.success(
        request,
        f"{product.name} is now {'available' if product.is_available else 'unavailable'}.",
    )
    return redirect("restaurants:menu_list", restaurant_id=restaurant.pk)


@owner_required
def opening_hours_edit(request, restaurant_id):
    restaurant = owned_restaurant_or_404(request, restaurant_id)
    current_hours = list(restaurant.opening_hours.all())

    if request.method == "POST":
        form = OpeningHoursForm(request.POST, opening_hours=current_hours)
        if form.is_valid():
            with transaction.atomic():
                for day_value, prefix in form.day_prefixes:
                    is_closed = form.cleaned_data[f"{prefix}_is_closed"]
                    OpeningHour.objects.update_or_create(
                        restaurant=restaurant,
                        day_of_week=day_value,
                        defaults={
                            "is_closed": is_closed,
                            "open_time": None
                            if is_closed
                            else form.cleaned_data[f"{prefix}_open_time"],
                            "close_time": None
                            if is_closed
                            else form.cleaned_data[f"{prefix}_close_time"],
                        },
                    )
            messages.success(request, "Opening hours saved.")
            return redirect(
                "restaurants:opening_hours",
                restaurant_id=restaurant.pk,
            )
    else:
        form = OpeningHoursForm(opening_hours=current_hours)

    return render(
        request,
        "restaurants/opening_hours_form.html",
        {"form": form, "restaurant": restaurant},
    )
