from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import SavedAddressForm
from .models import Customer


@login_required
def profile_and_addresses(request):
    is_admin = request.user.is_staff or request.user.is_superuser
    all_customers = None
    target_customer_id = request.GET.get("customer_id")

    if is_admin:
        all_customers = Customer.objects.select_related("user").order_by("user__username")
        if target_customer_id:
            customer = get_object_or_404(Customer, pk=target_customer_id)
        else:
            customer, _ = Customer._default_manager.get_or_create(
                user=request.user,
                defaults={"phone": ""},
            )
    else:
        customer, _ = Customer._default_manager.get_or_create(
            user=request.user,
            defaults={"phone": ""},
        )

    addresses = customer.addresses.select_related("zone").all()

    if request.method == "POST":
        form = SavedAddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.customer = customer
            address.save()
            if is_admin and target_customer_id:
                return redirect(f"/customers/?customer_id={customer.pk}")
            return redirect("customers:home")
    else:
        form = SavedAddressForm()

    return render(
        request,
        "customers/home.html",
        {
            "customer": customer,
            "addresses": addresses,
            "form": form,
            "is_admin": is_admin,
            "all_customers": all_customers,
        },
    )
