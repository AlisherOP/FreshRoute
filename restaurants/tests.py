import datetime
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
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


class RestaurantOwnerViewTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="menu_owner",
            email="menu_owner@example.com",
            password="pass",
            role=User.Role.OWNER,
        )
        self.restaurant = Restaurant.objects.create(
            owner=self.owner,
            name="Owner Restaurant",
            phone="+996555111222",
            address="Center Street 1",
        )
        self.category = FoodCategory.objects.create(
            restaurant=self.restaurant,
            name="Main dishes",
        )

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("restaurants:owner_dashboard"))
        self.assertRedirects(
            response,
            f"/accounts/login/?next={reverse('restaurants:owner_dashboard')}",
        )

    def test_customer_cannot_open_owner_dashboard(self):
        customer = User.objects.create_user(
            username="regular_customer",
            email="regular@example.com",
            password="pass",
            role=User.Role.CUSTOMER,
        )
        self.client.force_login(customer)
        response = self.client.get(reverse("restaurants:owner_dashboard"))
        self.assertEqual(response.status_code, 403)

    def test_owner_can_add_menu_item(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("restaurants:product_add", kwargs={"restaurant_id": self.restaurant.pk}),
            {
                "name": "Fresh Burger",
                "description": "Made to order",
                "category": self.category.pk,
                "price": "8.50",
                "is_vegetarian": "on",
            },
        )
        self.assertRedirects(
            response,
            reverse("restaurants:menu_list", kwargs={"restaurant_id": self.restaurant.pk}),
        )
        product = FoodProduct.objects.get(name="Fresh Burger")
        self.assertEqual(product.restaurant, self.restaurant)
        self.assertTrue(product.is_vegetarian)

    def test_owner_cannot_open_another_restaurants_menu(self):
        other_owner = User.objects.create_user(
            username="other_owner",
            email="other_owner@example.com",
            password="pass",
            role=User.Role.OWNER,
        )
        other_restaurant = Restaurant.objects.create(
            owner=other_owner,
            name="Other Restaurant",
            phone="+996555333444",
            address="North Ave 2",
        )
        self.client.force_login(self.owner)
        response = self.client.get(
            reverse("restaurants:menu_list", kwargs={"restaurant_id": other_restaurant.pk})
        )
        self.assertEqual(response.status_code, 404)

    def test_owner_can_toggle_product_availability(self):
        product = FoodProduct.objects.create(
            restaurant=self.restaurant,
            name="Soup",
            price="4.00",
        )
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse(
                "restaurants:product_toggle_availability",
                kwargs={"restaurant_id": self.restaurant.pk, "product_id": product.pk},
            )
        )
        product.refresh_from_db()
        self.assertFalse(product.is_available)
        self.assertRedirects(
            response,
            reverse("restaurants:menu_list", kwargs={"restaurant_id": self.restaurant.pk}),
        )

    def test_owner_can_save_the_weekly_opening_hours(self):
        self.client.force_login(self.owner)
        data = {}
        for day_value, day_label in OpeningHour.DayOfWeek.choices:
            prefix = day_label.lower()
            if day_value == OpeningHour.DayOfWeek.MONDAY:
                data[f"{prefix}_open_time"] = "09:00"
                data[f"{prefix}_close_time"] = "18:00"
            else:
                data[f"{prefix}_is_closed"] = "on"

        response = self.client.post(
            reverse("restaurants:opening_hours", kwargs={"restaurant_id": self.restaurant.pk}),
            data,
        )
        self.assertRedirects(
            response,
            reverse("restaurants:opening_hours", kwargs={"restaurant_id": self.restaurant.pk}),
        )
        self.assertEqual(self.restaurant.opening_hours.count(), 7)
        monday = self.restaurant.opening_hours.get(day_of_week=OpeningHour.DayOfWeek.MONDAY)
        self.assertFalse(monday.is_closed)
        self.assertEqual(monday.open_time.strftime("%H:%M"), "09:00")
        self.assertEqual(monday.close_time.strftime("%H:%M"), "18:00")

    def test_admin_can_access_owner_dashboard_and_see_all_owners(self):
        admin_user = User.objects.create_user(
            username="super_admin",
            email="admin@freshroute.com",
            password="pass",
            is_staff=True,
            is_superuser=True,
        )
        self.client.force_login(admin_user)
        response = self.client.get(reverse("restaurants:owner_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Restaurant Owners & Kitchens Directory")
        self.assertContains(response, self.owner.username)
        self.assertContains(response, "Enter As This Owner")

    def test_admin_can_enter_individual_owner_dashboard(self):
        admin_user = User.objects.create_user(
            username="super_admin_2",
            email="admin2@freshroute.com",
            password="pass",
            is_staff=True,
        )
        self.client.force_login(admin_user)
        response = self.client.get(
            reverse("restaurants:owner_dashboard") + f"?owner_id={self.owner.pk}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Admin Impersonation Mode")
        self.assertContains(response, self.restaurant.name)

    def test_admin_can_manage_any_restaurant_menu(self):
        admin_user = User.objects.create_user(
            username="super_admin_3",
            email="admin3@freshroute.com",
            password="pass",
            is_staff=True,
        )
        self.client.force_login(admin_user)
        response = self.client.get(
            reverse("restaurants:menu_list", kwargs={"restaurant_id": self.restaurant.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.restaurant.name)
