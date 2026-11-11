from django.db import models

# Create your models here.



class Customer(models.Model):

    customer_id = models.BigAutoField(primary_key=True)

    full_name = models.CharField(max_length=255)

    phone = models.CharField(max_length=25)

    email = models.EmailField(
        max_length=255,
        unique=True,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "customers"

    def __str__(self):
        return self.full_name
