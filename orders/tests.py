from datetime import timedelta
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from accounts.models import User
from customers.models import Customer
from orders.models import Coupon, Order, OrderItem, Review
from restaurants.models import Restaurant, FoodProduct


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
