from django.db import models


class Complaint(models.Model):
    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        RESOLVED = "RESOLVED", "Resolved"

    complaint_id = models.BigAutoField(primary_key=True)
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="complaints",
    )
    description = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
    )
    admin_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "complaints"

    def __str__(self):
        return f"Complaint #{self.complaint_id} on Order #{self.order_id}"
