from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from .models import Coupon, Order, OrderItem, Review


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("item_total",)
    fields = ("product", "quantity", "unit_price", "item_total")

    @admin.display(description="Total")
    def item_total(self, obj):
        if obj.pk:
            return f"${(obj.quantity * obj.unit_price):.2f}"
        return "—"


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "restaurant_scope",
        "discount_display",
        "usage_display",
        "valid_until",
        "status_badge",
    )
    list_filter = ("discount_type", "is_active")
    search_fields = ("code", "restaurant__name")
    actions = ["activate_coupons", "deactivate_coupons"]

    @admin.display(description="Restaurant Scope")
    def restaurant_scope(self, obj):
        return obj.restaurant.name if obj.restaurant else format_html('<span style="color: #2563eb; font-weight: 600;">Platform-Wide</span>')

    @admin.display(description="Discount")
    def discount_display(self, obj):
        if obj.discount_type == Coupon.DiscountType.PERCENT:
            return f"{obj.discount_value:.0f}% OFF"
        return f"${obj.discount_value:.2f} OFF"

    @admin.display(description="Usage")
    def usage_display(self, obj):
        max_str = str(obj.max_uses) if obj.max_uses is not None else "∞"
        return f"{obj.times_used} / {max_str}"

    @admin.display(description="Status")
    def status_badge(self, obj):
        if not obj.is_active:
            return format_html('<span style="color: #9ca3af;">Disabled</span>')
        if obj.valid_until < timezone.now():
            return format_html('<span style="color: #dc2626; font-weight: 600;">Expired</span>')
        return format_html('<span style="background-color: #d1fae5; color: #065f46; font-weight: 600; padding: 2px 8px; border-radius: 9999px; font-size: 11px;">Active</span>')

    @admin.action(description="Activate selected coupons")
    def activate_coupons(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description="Deactivate selected coupons")
    def deactivate_coupons(self, request, queryset):
        queryset.update(is_active=False)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_id",
        "customer",
        "restaurant",
        "status_badge",
        "payment_badge",
        "total_amount_display",
        "courier",
        "created_at",
    )
    list_filter = ("status", "payment_method", "payment_status", "created_at")
    search_fields = (
        "order_id",
        "customer__user__username",
        "customer__user__email",
        "restaurant__name",
        "stripe_payment_intent_id",
    )
    readonly_fields = (
        "order_id",
        "total_amount",
        "created_at",
        "updated_at",
        "accepted_at",
        "delivered_at",
        "cancelled_at",
        "stripe_payment_intent_id",
    )
    inlines = [OrderItemInline]
    actions = ["mark_accepted", "mark_cancelled"]

    @admin.display(description="Status", ordering="status")
    def status_badge(self, obj):
        colors = {
            Order.Status.PENDING: ("#92400e", "#fef3c7"),         # Amber
            Order.Status.ACCEPTED: ("#1e40af", "#dbeafe"),        # Blue
            Order.Status.PREPARING: ("#3730a3", "#e0e7ff"),       # Indigo
            Order.Status.READY: ("#155e75", "#cffafe"),           # Cyan
            Order.Status.OUT_FOR_DELIVERY: ("#6b21a8", "#f3e8ff"),# Purple
            Order.Status.DELIVERED: ("#065f46", "#d1fae5"),       # Green
            Order.Status.CANCELLED: ("#991b1b", "#fee2e2"),       # Red
        }
        fg, bg = colors.get(obj.status, ("#374151", "#f3f4f6"))
        return format_html(
            '<span style="background-color: {}; color: {}; font-weight: 600; padding: 3px 8px; border-radius: 9999px; font-size: 11px;">{}</span>',
            bg, fg, obj.get_status_display()
        )

    @admin.display(description="Payment", ordering="payment_status")
    def payment_badge(self, obj):
        colors = {
            Order.PaymentStatus.PAID: ("#065f46", "#d1fae5"),
            Order.PaymentStatus.UNPAID: ("#92400e", "#fef3c7"),
            Order.PaymentStatus.FAILED: ("#991b1b", "#fee2e2"),
            Order.PaymentStatus.REFUNDED: ("#475569", "#f1f5f9"),
        }
        fg, bg = colors.get(obj.payment_status, ("#374151", "#f3f4f6"))
        return format_html(
            '<span style="background-color: {}; color: {}; font-weight: 600; padding: 2px 6px; border-radius: 4px; font-size: 10px;">{} ({})</span>',
            bg, fg, obj.get_payment_status_display(), obj.get_payment_method_display()
        )

    @admin.display(description="Total", ordering="total_amount")
    def total_amount_display(self, obj):
        return format_html('<span style="font-weight: 700; font-family: monospace;">${:.2f}</span>', obj.total_amount)

    @admin.action(description="Transition selected to ACCEPTED")
    def mark_accepted(self, request, queryset):
        success, failed = 0, 0
        for order in queryset:
            try:
                order.set_status(Order.Status.ACCEPTED)
                success += 1
            except Exception:
                failed += 1
        self.message_user(request, f"Updated {success} order(s) to ACCEPTED ({failed} skipped due to invalid status transition).")

    @admin.action(description="Transition selected to CANCELLED")
    def mark_cancelled(self, request, queryset):
        success, failed = 0, 0
        for order in queryset:
            try:
                order.set_status(Order.Status.CANCELLED)
                success += 1
            except Exception:
                failed += 1
        self.message_user(request, f"Updated {success} order(s) to CANCELLED ({failed} skipped).")


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order_item_id", "order", "product", "quantity", "unit_price")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("review_id", "order", "star_rating", "comment_preview", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("order__order_id", "comment")
    readonly_fields = ("created_at",)

    @admin.display(description="Rating", ordering="rating")
    def star_rating(self, obj):
        stars = "★" * obj.rating + "☆" * (5 - obj.rating)
        return format_html('<span style="color: #f59e0b; font-size: 13px;">{}</span>', stars)

    @admin.display(description="Comment")
    def comment_preview(self, obj):
        if not obj.comment:
            return "—"
        return obj.comment[:60] + ("..." if len(obj.comment) > 60 else "")
