from django.conf import settings
from django.core.mail import send_mail


def send_order_status_email(order):
    recipient = order.customer.user.email
    if not recipient:
        return False

    subject = f"Update for your FreshRoute order #{order.pk}"
    message = (
        f"Hello {order.customer.user.username},\n\n"
        f"Your order from {order.restaurant.name} is now "
        f"{order.get_status_display().lower()}.\n\n"
        f"Thank you for ordering with FreshRoute."
    )
    return bool(
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient],
        )
    )
