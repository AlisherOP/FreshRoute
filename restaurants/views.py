from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import FoodProductForm
from .models import FoodProduct, Restaurant


def get_owned_restaurant(request, restaurant_id):
    return get_object_or_404(
        Restaurant,
        pk=restaurant_id,
        owner=request.user,
    )


@login_required
def owner_dashboard(request):
    restaurants = Restaurant.objects.filter(owner=request.user).order_by("name")
    return render(
        request,
        "restaurants/owner_dashboard.html",
        {"restaurants": restaurants},
    )


@login_required
def menu_list(request, restaurant_id):
    restaurant = get_owned_restaurant(request, restaurant_id)
    products = restaurant.products.filter(is_archived=False).select_related(
        "category"
    ).order_by("name")
    return render(
        request,
        "restaurants/menu_list.html",
        {"restaurant": restaurant, "products": products},
    )


@login_required
def product_add(request, restaurant_id):
    restaurant = get_owned_restaurant(request, restaurant_id)
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
            return redirect("restaurants:menu_list", restaurant_id=restaurant.pk)
    else:
        form = FoodProductForm(restaurant=restaurant)

    return render(
        request,
        "restaurants/product_form.html",
        {"form": form, "restaurant": restaurant, "page_title": "Add menu item"},
    )


@login_required
def product_edit(request, restaurant_id, product_id):
    restaurant = get_owned_restaurant(request, restaurant_id)
    product = get_object_or_404(
        FoodProduct,
        pk=product_id,
        restaurant=restaurant,
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
            return redirect("restaurants:menu_list", restaurant_id=restaurant.pk)
    else:
        form = FoodProductForm(instance=product, restaurant=restaurant)

    return render(
        request,
        "restaurants/product_form.html",
        {"form": form, "restaurant": restaurant, "page_title": "Edit menu item"},
    )


@login_required
@require_POST
def product_toggle_availability(request, restaurant_id, product_id):
    restaurant = get_owned_restaurant(request, restaurant_id)
    product = get_object_or_404(
        FoodProduct,
        pk=product_id,
        restaurant=restaurant,
        is_archived=False,
    )
    product.is_available = not product.is_available
    product.save(update_fields=["is_available"])
    return HttpResponseRedirect(
        reverse("restaurants:menu_list", kwargs={"restaurant_id": restaurant.pk})
    )
