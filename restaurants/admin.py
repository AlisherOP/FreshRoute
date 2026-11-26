from django.contrib import admin
from django.utils.html import format_html
from .models import Restaurant, OpeningHour, FoodCategory, FoodProduct


class OpeningHourInline(admin.TabularInline):
    model = OpeningHour
    extra = 1
    fields = ("day_of_week", "open_time", "close_time", "is_closed")


class FoodCategoryInline(admin.TabularInline):
    model = FoodCategory
    extra = 1


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = (
        "restaurant_id",
        "name",
        "owner",
        "phone",
        "approval_badge",
        "active_badge",
        "open_now_badge",
        "created_at",
    )
    list_filter = ("is_approved", "is_active")
    search_fields = ("name", "phone", "owner__username", "address")
    readonly_fields = ("created_at",)
    inlines = [OpeningHourInline, FoodCategoryInline]
    actions = [
        "approve_restaurants",
        "suspend_restaurants",
        "activate_restaurants",
        "deactivate_restaurants",
    ]

    @admin.display(description="Approval Status", ordering="is_approved")
    def approval_badge(self, obj):
        if obj.is_approved:
            return format_html(
                '<span style="background-color: #d1fae5; color: #065f46; font-weight: 600; padding: 2px 8px; border-radius: 9999px; font-size: 11px;">✓ Approved</span>'
            )
        return format_html(
            '<span style="background-color: #fee2e2; color: #991b1b; font-weight: 600; padding: 2px 8px; border-radius: 9999px; font-size: 11px;">⏳ Pending Approval</span>'
        )

    @admin.display(description="Active", ordering="is_active")
    def active_badge(self, obj):
        if obj.is_active:
            return format_html('<span style="color: #047857; font-weight: bold;">Yes</span>')
        return format_html('<span style="color: #991b1b; font-weight: bold;">No</span>')

    @admin.display(description="Currently Open")
    def open_now_badge(self, obj):
        if obj.is_open_now():
            return format_html(
                '<span style="background-color: #ecfdf5; color: #047857; border: 1px solid #a7f3d0; font-weight: 600; padding: 2px 6px; border-radius: 4px; font-size: 10px;">OPEN NOW</span>'
            )
        return format_html(
            '<span style="background-color: #f3f4f6; color: #6b7280; font-weight: 500; padding: 2px 6px; border-radius: 4px; font-size: 10px;">CLOSED</span>'
        )

    @admin.action(description="✓ Approve selected restaurants")
    def approve_restaurants(self, request, queryset):
        count = queryset.update(is_approved=True)
        self.message_user(request, f"Successfully approved {count} restaurant(s).")

    @admin.action(description="✕ Suspend / Revoke approval of selected restaurants")
    def suspend_restaurants(self, request, queryset):
        count = queryset.update(is_approved=False)
        self.message_user(request, f"Revoked approval for {count} restaurant(s).")

    @admin.action(description="Enable selected restaurants (is_active=True)")
    def activate_restaurants(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f"Activated {count} restaurant(s).")

    @admin.action(description="Disable selected restaurants (is_active=False)")
    def deactivate_restaurants(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f"Deactivated {count} restaurant(s).")


@admin.register(OpeningHour)
class OpeningHourAdmin(admin.ModelAdmin):
    list_display = ("restaurant", "day_of_week", "open_time", "close_time", "is_closed")
    list_filter = ("day_of_week", "is_closed", "restaurant")


@admin.register(FoodCategory)
class FoodCategoryAdmin(admin.ModelAdmin):
    list_display = ("category_id", "restaurant", "name", "product_count")
    list_filter = ("restaurant",)
    search_fields = ("name", "restaurant__name")

    @admin.display(description="Products")
    def product_count(self, obj):
        return obj.products.count()


@admin.register(FoodProduct)
class FoodProductAdmin(admin.ModelAdmin):
    list_display = (
        "product_id",
        "image_preview",
        "name",
        "restaurant",
        "category",
        "price_display",
        "dietary_badge",
        "availability_badge",
    )
    list_filter = ("is_available", "is_archived", "is_vegetarian", "restaurant")
    search_fields = ("name", "restaurant__name", "description")
    actions = ["mark_available", "mark_sold_out", "archive_products"]

    @admin.display(description="Photo")
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 36px; height: 36px; object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return "—"

    @admin.display(description="Price", ordering="price")
    def price_display(self, obj):
        return f"${obj.price:.2f}"

    @admin.display(description="Dietary")
    def dietary_badge(self, obj):
        if obj.is_vegetarian:
            return format_html(
                '<span style="background-color: #ecfdf5; color: #047857; font-weight: 600; padding: 2px 6px; border-radius: 4px; font-size: 10px;">VEG</span>'
            )
        return "—"

    @admin.display(description="Availability", ordering="is_available")
    def availability_badge(self, obj):
        if obj.is_archived:
            return format_html('<span style="color: #9ca3af; font-style: italic;">Archived</span>')
        if obj.is_available:
            return format_html('<span style="color: #047857; font-weight: 600;">In Stock</span>')
        return format_html('<span style="color: #dc2626; font-weight: 600;">Sold Out</span>')

    @admin.action(description="Mark selected items as In Stock")
    def mark_available(self, request, queryset):
        queryset.update(is_available=True)

    @admin.action(description="Mark selected items as Sold Out (Unavailable)")
    def mark_sold_out(self, request, queryset):
        queryset.update(is_available=False)

    @admin.action(description="Archive selected items")
    def archive_products(self, request, queryset):
        queryset.update(is_archived=True, is_available=False)
