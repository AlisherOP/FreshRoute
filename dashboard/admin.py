from django.contrib import admin
from .models import Complaint


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ("complaint_id", "order", "status", "created_at", "resolved_at")
    list_filter = ("status",)
    search_fields = ("order__order_id", "description", "admin_notes")
