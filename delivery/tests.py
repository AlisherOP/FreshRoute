from decimal import Decimal
from django.test import TestCase
from accounts.models import User
from delivery.models import Courier, DeliveryZone


class DeliveryModelTests(TestCase):
    def test_courier_creation(self):
        courier_user = User.objects.create_user(
            username="courier_bob",
            email="bob@delivery.com",
            password="pass",
            role=User.Role.COURIER,
        )
        courier = Courier.objects.create(
            user=courier_user,
            phone="+996777000111",
            is_available=True,
        )
        self.assertEqual(str(courier), "courier_bob")
        self.assertTrue(courier.is_available)

    def test_delivery_zone_creation(self):
        zone = DeliveryZone.objects.create(
            name="Downtown",
            fee=Decimal("4.50"),
        )
        self.assertEqual(str(zone), "Downtown (4.50)")
