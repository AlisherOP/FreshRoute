from django.contrib import admin
from .models import Customer, SavedAddress


class SavedAddressInline(admin.TabularInline):
    model = SavedAddress
    extra = 0


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("customer_id", "user", "phone", "created_at")
    search_fields = ("user__username", "user__email", "phone")
    inlines = [SavedAddressInline]


@admin.register(SavedAddress)
class SavedAddressAdmin(admin.ModelAdmin):
    list_display = ("address_id", "customer", "label", "zone", "is_default")
    list_filter = ("is_default", "zone")
    search_fields = ("customer__user__username", "label", "street_address")
