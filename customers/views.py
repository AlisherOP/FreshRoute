from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import SavedAddressForm
from .models import Customer


@login_required
def profile_and_addresses(request):
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
        },
    )
