from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Restaurant(models.Model):
    restaurant_id = models.BigAutoField(primary_key=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        limit_choices_to={"role": "OWNER"},
        related_name="owned_restaurants",
    )
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=25)
    address = models.TextField()
    description = models.TextField(null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "restaurants"

    def is_open_now(self):
        if not (self.is_approved and self.is_active):
            return False

        now = timezone.localtime()
        today = now.weekday()
        yesterday = (today - 1) % 7
        current_time = now.time()

        hours = self.opening_hours.all()

        today_hours = next(
            (h for h in hours if h.day_of_week == today and not h.is_closed), None)
        if today_hours and today_hours.open_time and today_hours.close_time:
            if today_hours.open_time <= today_hours.close_time:
                if today_hours.open_time <= current_time <= today_hours.close_time:
                    return True
            elif current_time >= today_hours.open_time:
                return True

        yesterday_hours = next(
            (h for h in hours if h.day_of_week == yesterday and not h.is_closed), None)
        if yesterday_hours and yesterday_hours.open_time and yesterday_hours.close_time:
            if yesterday_hours.close_time < yesterday_hours.open_time:
                if current_time <= yesterday_hours.close_time:
                    return True

        return False

    def __str__(self):
        return self.name


class OpeningHour(models.Model):
    class DayOfWeek(models.IntegerChoices):
        MONDAY = 0, "Monday"
        TUESDAY = 1, "Tuesday"
        WEDNESDAY = 2, "Wednesday"
        THURSDAY = 3, "Thursday"
        FRIDAY = 4, "Friday"
        SATURDAY = 5, "Saturday"
        SUNDAY = 6, "Sunday"

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="opening_hours",
    )
    day_of_week = models.IntegerField(choices=DayOfWeek.choices)
    open_time = models.TimeField(null=True, blank=True)
    close_time = models.TimeField(null=True, blank=True)
    is_closed = models.BooleanField(default=False)

    class Meta:
        db_table = "opening_hours"
        constraints = [
            models.UniqueConstraint(
                fields=["restaurant", "day_of_week"],
                name="unique_restaurant_day",
            ),
            models.CheckConstraint(
                condition=models.Q(is_closed=True)
                | (models.Q(open_time__isnull=False) & models.Q(close_time__isnull=False)),
                name="opening_hours_required_when_open",
            ),
        ]

    def clean(self):
        if not self.is_closed and (self.open_time is None or self.close_time is None):
            raise ValidationError(
                "Open and close times are required unless marked closed.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_day_of_week_display()}"


class FoodCategory(models.Model):
    category_id = models.BigAutoField(primary_key=True)
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="categories",
    )
    name = models.CharField(max_length=100)

    class Meta:
        db_table = "food_categories"
        constraints = [
            models.UniqueConstraint(
                fields=["restaurant", "name"],
                name="unique_category_per_restaurant",
            )
        ]

    def __str__(self):
        return self.name


class FoodProduct(models.Model):
    product_id = models.BigAutoField(primary_key=True)
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.RESTRICT,
        related_name="products",
    )
    category = models.ForeignKey(
        FoodCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="products/", null=True, blank=True)
    is_vegetarian = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)

    class Meta:
        db_table = "food_products"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(price__gte=0),
                name="product_price_non_negative",
            )
        ]

    def clean(self):
        if self.category_id and self.category.restaurant_id != self.restaurant_id:
            raise ValidationError(
                "Selected category does not belong to this restaurant.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
