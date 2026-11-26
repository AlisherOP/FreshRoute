from django.contrib import admin
from django.utils.html import format_html
from .models import DeliveryZone, Courier


@admin.register(DeliveryZone)
class DeliveryZoneAdmin(admin.ModelAdmin):
    list_display = ("zone_id", "name", "fee_display", "active_badge", "address_count")
    list_filter = ("is_active",)
    search_fields = ("name",)
    actions = ["activate_zones", "deactivate_zones"]

    @admin.display(description="Delivery Fee", ordering="fee")
    def fee_display(self, obj):
        return f"${obj.fee:.2f}"

    @admin.display(description="Status", ordering="is_active")
    def active_badge(self, obj):
        if obj.is_active:
            return format_html('<span style="color: #047857; font-weight: 600;">Active</span>')
        return format_html('<span style="color: #dc2626; font-weight: 600;">Disabled</span>')

    @admin.display(description="Saved Addresses")
    def address_count(self, obj):
        return obj.addresses.count()

    @admin.action(description="Enable selected delivery zones")
    def activate_zones(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description="Disable selected delivery zones")
    def deactivate_zones(self, request, queryset):
        queryset.update(is_active=False)


@admin.register(Courier)
class CourierAdmin(admin.ModelAdmin):
    list_display = ("courier_id", "user", "phone", "availability_badge", "deliveries_count")
    list_filter = ("is_available",)
    search_fields = ("user__username", "user__email", "phone")
    actions = ["set_available", "set_offline"]

    @admin.display(description="Status", ordering="is_available")
    def availability_badge(self, obj):
        if obj.is_available:
            return format_html(
                '<span style="background-color: #d1fae5; color: #065f46; font-weight: 600; padding: 2px 8px; border-radius: 9999px; font-size: 11px;">● Available for Orders</span>'
            )
        return format_html(
            '<span style="background-color: #f3f4f6; color: #6b7280; font-weight: 500; padding: 2px 8px; border-radius: 9999px; font-size: 11px;">Offline</span>'
        )

    @admin.display(description="Total Deliveries")
    def deliveries_count(self, obj):
        return obj.deliveries.count()

    @admin.action(description="Set selected couriers Available")
    def set_available(self, request, queryset):
        queryset.update(is_available=True)

    @admin.action(description="Set selected couriers Offline")
    def set_offline(self, request, queryset):
        queryset.update(is_available=False)
