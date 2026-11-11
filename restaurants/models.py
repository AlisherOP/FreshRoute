from django.db import models

# Create your models here.
class Restaurant(models.Model):
    restaurant_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length =255)
    phone = models.CharField(max_length=25)
    address=models.TextField()
    description=models.TextField(null=True, blank=True)
    is_active=models.BooleanField(default=True)

    class Meta:
        db_table = "restaurants"

    def __str__(self):
        return self.name





class FoodCategory(models.Model):

    category_id = models.BigAutoField(primary_key=True)

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="categories"
    )

    name = models.CharField(max_length=100)

    class Meta:
        db_table = "food_categories"

        constraints = [
            models.UniqueConstraint(
                fields=["restaurant", "name"],
                name="unique_category_per_restaurant"
            ),
            models.UniqueConstraint(
                fields=["category_id", "restaurant"],
                name="unique_category_restaurant_pair"
            )
        ]

    def __str__(self):
        return self.name


class FoodProduct(models.Model):

    product_id = models.BigAutoField(primary_key=True)

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.RESTRICT,
        related_name="products"
    )

    category = models.ForeignKey(
        FoodCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products"
    )

    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)

    class Meta:
        db_table = "food_products"

        constraints = [
            models.CheckConstraint(
                condition=models.Q(price__gte=0),
                name="product_price_non_negative"
            )
        ]

    def __str__(self):
        return self.name

