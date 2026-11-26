from django.test import TestCase
from accounts.models import User
from customers.models import Customer, SavedAddress
from delivery.models import DeliveryZone


class CustomerModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test_customer",
            email="cust@example.com",
            password="pass",
            role=User.Role.CUSTOMER,
        )
        self.customer = Customer.objects.create(
            user=self.user,
            phone="+996555123456",
        )
        self.zone = DeliveryZone.objects.create(name="Center", fee=5.00)

    def test_customer_str(self):
        self.assertEqual(str(self.customer), "test_customer")

    def test_single_default_address_switch(self):
        addr1 = SavedAddress.objects.create(
            customer=self.customer,
            zone=self.zone,
            label="Home",
            street_address="123 Main St",
            is_default=True,
        )
        addr2 = SavedAddress.objects.create(
            customer=self.customer,
            zone=self.zone,
            label="Work",
            street_address="456 Office Ave",
            is_default=True,
        )
        addr1.refresh_from_db()
        self.assertFalse(addr1.is_default)
        self.assertTrue(addr2.is_default)
