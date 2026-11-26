from django.contrib import admin
from .models import Restaurant, OpeningHour, FoodCategory, FoodProduct


class OpeningHourInline(admin.TabularInline):
    model = OpeningHour
    extra = 1


class FoodCategoryInline(admin.TabularInline):
    model = FoodCategory
    extra = 1


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ("restaurant_id", "name", "owner", "phone", "is_approved", "is_active", "created_at")
    list_filter = ("is_approved", "is_active")
    search_fields = ("name", "phone", "owner__username")
    inlines = [OpeningHourInline, FoodCategoryInline]


@admin.register(OpeningHour)
class OpeningHourAdmin(admin.ModelAdmin):
    list_display = ("restaurant", "day_of_week", "open_time", "close_time", "is_closed")
    list_filter = ("day_of_week", "is_closed", "restaurant")


@admin.register(FoodCategory)
class FoodCategoryAdmin(admin.ModelAdmin):
    list_display = ("category_id", "restaurant", "name")
    list_filter = ("restaurant",)
    search_fields = ("name", "restaurant__name")


@admin.register(FoodProduct)
class FoodProductAdmin(admin.ModelAdmin):
    list_display = ("product_id", "name", "restaurant", "category", "price", "is_available", "is_archived")
    list_filter = ("is_available", "is_archived", "is_vegetarian", "restaurant")
    search_fields = ("name", "restaurant__name")
