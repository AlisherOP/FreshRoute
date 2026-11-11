
from django.db import models


class Order(models.Model):

    class OrderStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        CONFIRMED = "CONFIRMED", "Confirmed"
        PREPARING = "PREPARING", "Preparing"
        OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY", "Out for delivery"
        DELIVERED = "DELIVERED", "Delivered"
        CANCELLED = "CANCELLED", "Cancelled"

    class PaymentMethod(models.TextChoices):
        CASH = "CASH", "Cash"
        CARD = "CARD", "Card"

    class PaymentStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PAID = "PAID", "Paid"
        FAILED = "FAILED", "Failed"
        REFUNDED = "REFUNDED", "Refunded"

    order_id = models.BigAutoField(primary_key=True)

    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.RESTRICT,
        related_name="orders"
    )

    restaurant = models.ForeignKey(
        "restaurants.Restaurant",
        on_delete=models.RESTRICT,
        related_name="orders"
    )

    status = models.CharField(
        max_length=30,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING
    )

    delivery_address = models.TextField()

    delivery_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CASH
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "orders"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(delivery_fee__gte=0),
                name="order_delivery_fee_non_negative"
            ),
            models.UniqueConstraint(
                fields=["order_id", "restaurant"],
                name="unique_order_restaurant_pair"
            )
        ]

    def __str__(self):
        return f"Order #{self.order_id}"


class OrderItem(models.Model):

    order_item_id = models.BigAutoField(primary_key=True)

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        db_constraint=False
    )

    product = models.ForeignKey(
        "restaurants.FoodProduct",
        on_delete=models.RESTRICT,
        related_name="order_items",
        db_constraint=False
    )

    restaurant = models.ForeignKey(
        "restaurants.Restaurant",
        on_delete=models.RESTRICT,
        related_name="order_items"
    )

    quantity = models.PositiveIntegerField()

    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    class Meta:
        db_table = "order_items"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(quantity__gt=0),
                name="order_item_quantity_positive"
            ),
            models.CheckConstraint(
                condition=models.Q(unit_price__gte=0),
                name="order_item_price_non_negative"
            ),
            models.UniqueConstraint(
                fields=["order", "product"],
                name="unique_product_per_order"
            )
        ]

    def __str__(self):
        return f"Order item #{self.order_item_id}"
