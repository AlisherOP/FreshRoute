from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from .models import Complaint


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = (
        "complaint_id",
        "order_reference",
        "status_badge",
        "description_preview",
        "created_at",
        "resolved_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("order__order_id", "description", "admin_notes")
    readonly_fields = ("created_at", "resolved_at")
    actions = ["mark_in_progress", "mark_resolved"]

    @admin.display(description="Order Ref", ordering="order__order_id")
    def order_reference(self, obj):
        return f"Order #{obj.order.order_id} ({obj.order.customer.user.username})"

    @admin.display(description="Status", ordering="status")
    def status_badge(self, obj):
        colors = {
            Complaint.Status.OPEN: ("#991b1b", "#fee2e2"),         # Red
            Complaint.Status.IN_PROGRESS: ("#92400e", "#fef3c7"),  # Amber
            Complaint.Status.RESOLVED: ("#065f46", "#d1fae5"),     # Green
        }
        fg, bg = colors.get(obj.status, ("#374151", "#f3f4f6"))
        return format_html(
            '<span style="background-color: {}; color: {}; font-weight: 600; padding: 2px 8px; border-radius: 9999px; font-size: 11px;">{}</span>',
            bg, fg, obj.get_status_display()
        )

    @admin.display(description="Complaint Description")
    def description_preview(self, obj):
        return obj.description[:70] + ("..." if len(obj.description) > 70 else "")

    @admin.action(description="Mark selected complaints as In Progress")
    def mark_in_progress(self, request, queryset):
        count = queryset.update(status=Complaint.Status.IN_PROGRESS)
        self.message_user(request, f"Updated {count} complaint(s) to IN PROGRESS.")

    @admin.action(description="✓ Mark selected complaints as RESOLVED")
    def mark_resolved(self, request, queryset):
        now = timezone.now()
        count = queryset.update(status=Complaint.Status.RESOLVED, resolved_at=now)
        self.message_user(request, f"Marked {count} complaint(s) as RESOLVED at {now.strftime('%H:%M:%S')}.")
