
# Create your models here.

from django.conf import settings
from django.db import models


class DeliveryZone(models.Model):
    zone_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    fee = models.DecimalField(max_digits=8, decimal_places=2)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "delivery_zones"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(fee__gte=0),
                name="delivery_zone_fee_non_negative",
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.fee})"


class Courier(models.Model):
    courier_id = models.BigAutoField(primary_key=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={"role": "COURIER"},
        related_name="courier_profile",
    )
    phone = models.CharField(max_length=25)
    is_available = models.BooleanField(default=True)

    class Meta:
        db_table = "couriers"

    def __str__(self):
        return self.user.get_full_name() or self.user.username
