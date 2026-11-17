from django.contrib import admin
from .models import Coupon, Order, OrderItem, Review


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ("code", "restaurant", "discount_type", "discount_value", "times_used", "max_uses", "valid_until", "is_active")
    list_filter = ("discount_type", "is_active")
    search_fields = ("code", "restaurant__name")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_id", "customer", "restaurant", "status", "payment_method", "payment_status", "total_amount", "created_at")
    list_filter = ("status", "payment_method", "payment_status")
    search_fields = ("order_id", "customer__user__username", "restaurant__name")
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order_item_id", "order", "product", "quantity", "unit_price")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("review_id", "order", "rating", "created_at")
    list_filter = ("rating",)
    search_fields = ("order__order_id", "comment")
