from django.contrib import admin
from .models import DeliveryZone, Courier


@admin.register(DeliveryZone)
class DeliveryZoneAdmin(admin.ModelAdmin):
    list_display = ("zone_id", "name", "fee", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(Courier)
class CourierAdmin(admin.ModelAdmin):
    list_display = ("courier_id", "user", "phone", "is_available")
    list_filter = ("is_available",)
    search_fields = ("user__username", "user__email", "phone")
