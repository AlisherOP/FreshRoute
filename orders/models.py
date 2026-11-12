from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q
from django.utils import timezone


class Coupon(models.Model):
    class DiscountType(models.TextChoices):
        PERCENT = "PERCENT", "Percentage"
        FIXED = "FIXED", "Fixed Amount"

    coupon_id = models.BigAutoField(primary_key=True)
    restaurant = models.ForeignKey(
        "restaurants.Restaurant",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="coupons",
        help_text="Leave blank for platform-wide coupons.",
    )
    code = models.CharField(max_length=30, unique=True)
    discount_type = models.CharField(
        max_length=10, choices=DiscountType.choices)
    discount_value = models.DecimalField(max_digits=8, decimal_places=2)
    min_order_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    max_uses = models.PositiveIntegerField(null=True, blank=True)
    times_used = models.PositiveIntegerField(default=0)
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "coupons"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(discount_value__gt=0)
                & (~models.Q(discount_type="PERCENT") | models.Q(discount_value__lte=100)),
                name="coupon_valid_discount_value",
            ),
            models.CheckConstraint(
                condition=models.Q(min_order_amount__gte=0),
                name="coupon_min_order_non_negative",
            ),
            models.CheckConstraint(
                condition=models.Q(max_uses__isnull=True) | models.Q(
                    times_used__lte=models.F("max_uses")),
                name="coupon_usage_within_limit",
            ),
        ]

    def consume(self):
        """Atomically increment usage to prevent race conditions during checkout."""
        updated = Coupon.objects.filter(pk=self.pk).filter(
            Q(max_uses__isnull=True) | Q(times_used__lt=F("max_uses"))
        ).update(times_used=F("times_used") + 1)
        return bool(updated)

    def save(self, *args, **kwargs):
        self.code = self.code.strip().upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.code


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        ACCEPTED = "ACCEPTED", "Accepted"
        PREPARING = "PREPARING", "Preparing"
        READY = "READY", "Ready"
        OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY", "Out for Delivery"
        DELIVERED = "DELIVERED", "Delivered"
        CANCELLED = "CANCELLED", "Cancelled"

    class PaymentMethod(models.TextChoices):
        STRIPE = "STRIPE", "Stripe"
        COD = "COD", "Cash on Delivery"

    class PaymentStatus(models.TextChoices):
        UNPAID = "UNPAID", "Unpaid"
        PAID = "PAID", "Paid"
        FAILED = "FAILED", "Failed"
        REFUNDED = "REFUNDED", "Refunded"

    ALLOWED_TRANSITIONS = {
        Status.PENDING: {Status.ACCEPTED, Status.CANCELLED},
        Status.ACCEPTED: {Status.PREPARING, Status.CANCELLED},
        Status.PREPARING: {Status.READY},
        Status.READY: {Status.OUT_FOR_DELIVERY},
        Status.OUT_FOR_DELIVERY: {Status.DELIVERED},
    }

    order_id = models.BigAutoField(primary_key=True)
    customer = models.ForeignKey(
        "customer.Customer",
        on_delete=models.RESTRICT,
        related_name="orders",
    )
    restaurant = models.ForeignKey(
        "restaurants.Restaurant",
        on_delete=models.RESTRICT,
        related_name="orders",
    )
    courier = models.ForeignKey(
        "delivery.Courier",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deliveries",
    )
    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING)
    delivery_address = models.TextField()
    notes = models.TextField(blank=True)

    payment_method = models.CharField(
        max_length=20, choices=PaymentMethod.choices)
    payment_status = models.CharField(
        max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.UNPAID)
    stripe_payment_intent_id = models.CharField(
        max_length=255, unique=True, null=True, blank=True)

    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    delivery_fee = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, editable=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "orders"
        indexes = [
            models.Index(fields=["restaurant", "status"]),
            models.Index(fields=["created_at"]),
        ]
        constraints = [
            models.CheckConstraint(condition=models.Q(
                subtotal__gte=0), name="order_subtotal_non_negative"),
            models.CheckConstraint(condition=models.Q(
                discount_amount__gte=0), name="order_discount_non_negative"),
            models.CheckConstraint(condition=models.Q(
                delivery_fee__gte=0), name="order_delivery_fee_non_negative"),
            models.CheckConstraint(condition=models.Q(
                total_amount__gte=0), name="order_total_non_negative"),
            models.CheckConstraint(condition=models.Q(discount_amount__lte=models.F(
                "subtotal")), name="order_discount_lte_subtotal"),
        ]

    def set_status(self, new_status):
        if new_status not in self.ALLOWED_TRANSITIONS.get(self.status, set()):
            raise ValidationError(
                f"Cannot change {self.status} → {new_status}")
        self.status = new_status
        now = timezone.now()
        update_fields = ["status", "updated_at"]

        if new_status == self.Status.ACCEPTED:
            self.accepted_at = now
            update_fields.append("accepted_at")
        elif new_status == self.Status.DELIVERED:
            self.delivered_at = now
            update_fields.append("delivered_at")
        elif new_status == self.Status.CANCELLED:
            self.cancelled_at = now
            update_fields.append("cancelled_at")

        self.save(update_fields=update_fields)

    def clean(self):
        if self.coupon_id and self.coupon.restaurant_id and self.coupon.restaurant_id != self.restaurant_id:
            raise ValidationError(
                "This coupon is not valid for this restaurant.")

    def save(self, *args, **kwargs):
        # Prevent rewriting total_amount if we are only updating specific fields via set_status()
        if not kwargs.get("update_fields") or "total_amount" in kwargs.get("update_fields"):
            self.total_amount = self.subtotal - self.discount_amount + self.delivery_fee
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.order_id} ({self.get_status_display()})"


class OrderItem(models.Model):
    order_item_id = models.BigAutoField(primary_key=True)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        "restaurants.FoodProduct",
        on_delete=models.RESTRICT,
        related_name="order_items",
    )
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = "order_items"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(quantity__gte=1),
                name="order_item_qty_min_1",
            ),
            models.CheckConstraint(
                condition=models.Q(unit_price__gte=0),
                name="order_item_unit_price_non_negative",
            ),
        ]

    def clean(self):
        if self.order_id and self.product_id and self.product.restaurant_id != self.order.restaurant_id:
            raise ValidationError(
                "Order item product must belong to the order's restaurant.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"


class Review(models.Model):
    review_id = models.BigAutoField(primary_key=True)
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="review",
    )
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "reviews"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(rating__gte=1, rating__lte=5),
                name="review_rating_1_5",
            )
        ]

    def clean(self):
        if self.order_id and self.order.status != Order.Status.DELIVERED:
            raise ValidationError(
                "Reviews can only be left on delivered orders.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Review for Order #{self.order_id} ({self.rating}/5)"
