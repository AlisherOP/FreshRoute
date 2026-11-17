from django.test import TestCase
from accounts.models import User


class UserModelTests(TestCase):
    def test_create_user_with_role(self):
        user = User.objects.create_user(
            username="owner_user",
            email="owner@example.com",
            password="securepassword123",
            role=User.Role.OWNER,
        )
        self.assertEqual(user.role, User.Role.OWNER)
        self.assertEqual(str(user), "owner_user (Restaurant Owner)")

    def test_default_role_is_customer(self):
        user = User.objects.create_user(
            username="regular_user",
            email="regular@example.com",
            password="securepassword123",
        )
        self.assertEqual(user.role, User.Role.CUSTOMER)
