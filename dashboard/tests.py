from datetime import time
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from customers.models import Customer
from dashboard.models import Complaint
from delivery.models import Courier
from orders.models import Order
from restaurants.models import Restaurant, OpeningHour


class OpsDashboardTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a regular customer
        self.regular_user = User.objects.create_user(
            username="regular_cust",
            email="cust@test.com",
            password="password123",
            role=User.Role.CUSTOMER,
        )
        # Create a staff admin user
        self.staff_user = User.objects.create_user(
            username="staff_admin",
            email="staff@test.com",
            password="password123",
            is_staff=True,
        )
        # Create a restaurant owner & restaurants
        self.owner = User.objects.create_user(
            username="owner_mike",
            email="mike@rest.com",
            password="password123",
            role=User.Role.OWNER,
        )
        # 1. An open & approved restaurant for placing orders
        self.open_restaurant = Restaurant.objects.create(
            owner=self.owner,
            name="Open Bistro",
            phone="+996555123120",
            address="Alley 1",
            is_approved=True,
            is_active=True,
        )
        for day_value, _ in OpeningHour.DayOfWeek.choices:
            OpeningHour.objects.create(
                restaurant=self.open_restaurant,
                day_of_week=day_value,
                open_time=time.min,
                close_time=time.max,
            )

        # 2. A pending restaurant for testing approvals
        self.pending_restaurant = Restaurant.objects.create(
            owner=self.owner,
            name="Pending Bistro",
            phone="+996555123123",
            address="Alley 5",
            is_approved=False,
        )

        # Create a courier
        self.courier_user = User.objects.create_user(
            username="courier_dave",
            email="dave@courier.com",
            password="password123",
            role=User.Role.COURIER,
        )
        self.courier = Courier.objects.create(
            user=self.courier_user,
            phone="+996555888999",
            is_available=True,
        )
        # Create a customer & order
        self.customer = Customer.objects.create(
            user=self.regular_user,
            phone="+996555000111",
        )
        self.order = Order.objects.create(
            customer=self.customer,
            restaurant=self.open_restaurant,
            delivery_address="742 Evergreen Terrace",
            payment_method=Order.PaymentMethod.COD,
            subtotal=Decimal("25.00"),
        )
        self.complaint = Complaint.objects.create(
            order=self.order,
            description="Soup was cold on arrival",
            status=Complaint.Status.OPEN,
        )

    def test_ops_dashboard_requires_staff(self):
        # Unauthenticated user
        response = self.client.get(reverse("dashboard:ops_dashboard"))
        self.assertEqual(response.status_code, 302)

        # Authenticated non-staff user
        self.client.force_login(self.regular_user)
        response = self.client.get(reverse("dashboard:ops_dashboard"))
        self.assertEqual(response.status_code, 302)

        # Staff user gets 200
        self.client.force_login(self.staff_user)
        response = self.client.get(reverse("dashboard:ops_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "FreshRoute")
        self.assertContains(response, "Pending Bistro")
        self.assertContains(response, "Soup was cold on arrival")

    def test_approve_restaurant_action(self):
        self.client.force_login(self.staff_user)
        url = reverse("dashboard:approve_restaurant", args=[self.pending_restaurant.restaurant_id])
        response = self.client.post(url, {"action": "approve"})
        self.assertEqual(response.status_code, 302)
        self.pending_restaurant.refresh_from_db()
        self.assertTrue(self.pending_restaurant.is_approved)

    def test_update_complaint_action(self):
        self.client.force_login(self.staff_user)
        url = reverse("dashboard:update_complaint", args=[self.complaint.complaint_id])
        response = self.client.post(url, {
            "status": Complaint.Status.RESOLVED,
            "admin_notes": "Issued a $5 voucher to customer",
        })
        self.assertEqual(response.status_code, 302)
        self.complaint.refresh_from_db()
        self.assertEqual(self.complaint.status, Complaint.Status.RESOLVED)
        self.assertIsNotNone(self.complaint.resolved_at)
        self.assertEqual(self.complaint.admin_notes, "Issued a $5 voucher to customer")

    def test_assign_courier_action(self):
        self.client.force_login(self.staff_user)
        url = reverse("dashboard:assign_courier", args=[self.order.order_id])
        response = self.client.post(url, {"courier_id": self.courier.courier_id})
        self.assertEqual(response.status_code, 302)
        self.order.refresh_from_db()
        self.assertEqual(self.order.courier, self.courier)
