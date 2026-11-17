import datetime
from django.core.exceptions import ValidationError
from django.test import TestCase
from accounts.models import User
from restaurants.models import Restaurant, OpeningHour, FoodCategory, FoodProduct


class RestaurantModelTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner1",
            email="owner1@example.com",
            password="pass",
            role=User.Role.OWNER,
        )
        self.restaurant = Restaurant.objects.create(
            owner=self.owner,
            name="Tasty Bites",
            phone="+996555111222",
            address="Center Street 1",
            is_approved=True,
            is_active=True,
        )
        self.category = FoodCategory.objects.create(
            restaurant=self.restaurant,
            name="Burgers",
        )

    def test_category_must_belong_to_same_restaurant(self):
        other_restaurant = Restaurant.objects.create(
            owner=self.owner,
            name="Pizza Place",
            phone="+996555333444",
            address="North Ave 2",
        )
        product = FoodProduct(
            restaurant=other_restaurant,
            category=self.category,
            name="Cheeseburger",
            price=10.00,
        )
        with self.assertRaises(ValidationError):
            product.clean()

    def test_opening_hour_clean_validation(self):
        # Open requires times
        hour = OpeningHour(
            restaurant=self.restaurant,
            day_of_week=0,
            is_closed=False,
            open_time=None,
        )
        with self.assertRaises(ValidationError):
            hour.clean()
