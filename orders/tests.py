from datetime import time, timedelta
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from accounts.models import User
from customers.models import Customer
from orders.models import Coupon, Order, OrderItem, Review
from restaurants.models import Restaurant, FoodProduct, OpeningHour


class OrderModelTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="rest_owner",
            email="rest_owner@example.com",
            password="pass",
            role=User.Role.OWNER,
        )
        self.restaurant = Restaurant.objects.create(
            owner=self.owner,
            name="Fast Food Express",
            phone="+996555999888",
            address="South St 9",
            is_approved=True,
            is_active=True,
        )
        for day_value, _ in OpeningHour.DayOfWeek.choices:
            OpeningHour.objects.create(
                restaurant=self.restaurant,
                day_of_week=day_value,
                open_time=time.min,
                close_time=time.max,
            )
        self.customer_user = User.objects.create_user(
            username="buyer",
            email="buyer@example.com",
            password="pass",
            role=User.Role.CUSTOMER,
        )
        self.customer = Customer.objects.create(
            user=self.customer_user,
            phone="+996555777888",
        )
        self.product = FoodProduct.objects.create(
            restaurant=self.restaurant,
            name="Combo Meal",
            price=Decimal("15.00"),
        )
        self.coupon = Coupon.objects.create(
            restaurant=self.restaurant,
            code="SAVE5",
            discount_type=Coupon.DiscountType.FIXED,
            discount_value=Decimal("5.00"),
            valid_until=timezone.now() + timedelta(days=7),
            max_uses=2,
        )

    def test_order_total_calculation(self):
        order = Order.objects.create(
            customer=self.customer,
            restaurant=self.restaurant,
            delivery_address="My Apartment",
            payment_method=Order.PaymentMethod.COD,
            subtotal=Decimal("30.00"),
            discount_amount=Decimal("5.00"),
            delivery_fee=Decimal("3.00"),
        )
        self.assertEqual(order.total_amount, Decimal("28.00"))

    def test_order_status_transitions(self):
        order = Order.objects.create(
            customer=self.customer,
            restaurant=self.restaurant,
            delivery_address="My Apartment",
            payment_method=Order.PaymentMethod.COD,
            subtotal=Decimal("30.00"),
        )
        # PENDING -> ACCEPTED is allowed
        order.set_status(Order.Status.ACCEPTED)
        self.assertEqual(order.status, Order.Status.ACCEPTED)
        self.assertIsNotNone(order.accepted_at)

        # ACCEPTED -> DELIVERED directly is NOT allowed
        with self.assertRaises(ValidationError):
            order.set_status(Order.Status.DELIVERED)

    def test_coupon_atomic_consume(self):
        self.assertTrue(self.coupon.consume())
        self.coupon.refresh_from_db()
        self.assertEqual(self.coupon.times_used, 1)

        self.assertTrue(self.coupon.consume())
        self.coupon.refresh_from_db()
        self.assertEqual(self.coupon.times_used, 2)

        # Exceeded max_uses
        self.assertFalse(self.coupon.consume())

    def test_review_only_for_delivered_orders(self):
        order = Order.objects.create(
            customer=self.customer,
            restaurant=self.restaurant,
            delivery_address="My Apartment",
            payment_method=Order.PaymentMethod.COD,
            subtotal=Decimal("20.00"),
            status=Order.Status.PENDING,
        )
        review = Review(
            order=order,
            rating=5,
            comment="Great food!",
        )
        with self.assertRaises(ValidationError):
            review.clean()

    def test_closed_restaurant_rejects_new_order(self):
        self.restaurant.is_active = False
        self.restaurant.save(update_fields=["is_active"])
        with self.assertRaises(ValidationError):
            Order.objects.create(
                customer=self.customer,
                restaurant=self.restaurant,
                delivery_address="My Apartment",
                payment_method=Order.PaymentMethod.COD,
                subtotal=Decimal("10.00"),
            )

    def test_owner_status_change_sends_customer_email(self):
        order = Order.objects.create(
            customer=self.customer,
            restaurant=self.restaurant,
            delivery_address="My Apartment",
            payment_method=Order.PaymentMethod.COD,
            subtotal=Decimal("10.00"),
        )
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse(
                "orders:change_order_status",
                kwargs={"restaurant_id": self.restaurant.pk, "order_id": order.pk},
            ),
            {"status": Order.Status.ACCEPTED},
        )
        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.ACCEPTED)
        self.assertRedirects(
            response,
            reverse("orders:incoming_orders", kwargs={"restaurant_id": self.restaurant.pk}),
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.customer_user.email])
        self.assertIn("accepted", mail.outbox[0].body.lower())
