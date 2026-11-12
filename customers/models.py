from django.conf import settings
from django.db import models, transaction


class Customer(models.Model):
    customer_id = models.BigAutoField(primary_key=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="customer_profile",
    )
    phone = models.CharField(max_length=25)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "customers"

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class SavedAddress(models.Model):
    address_id = models.BigAutoField(primary_key=True)
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="addresses",
    )
    zone = models.ForeignKey(
        "delivery.DeliveryZone",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="addresses",
    )
    label = models.CharField(max_length=50, help_text="e.g., Home, Work, Dorm")
    street_address = models.TextField()
    is_default = models.BooleanField(default=False)

    class Meta:
        db_table = "saved_addresses"
        constraints = [
            models.UniqueConstraint(
                fields=["customer"],
                condition=models.Q(is_default=True),
                name="one_default_address_per_customer",
            )
        ]

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if self.is_default:
                SavedAddress.objects.filter(
                    customer=self.customer,
                    is_default=True,
                ).exclude(pk=self.pk).update(is_default=False)
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.label}: {self.street_address[:40]}"
