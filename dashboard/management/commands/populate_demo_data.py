from datetime import time, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import User
from customers.models import Customer, SavedAddress
from dashboard.models import Complaint
from delivery.models import Courier, DeliveryZone
from orders.models import Coupon, Order, OrderItem
from restaurants.models import FoodCategory, FoodProduct, OpeningHour, Restaurant


class Command(BaseCommand):
    help = "Seeds realistic demo data for the FreshRoute Operations Dashboard"

    def handle(self, *args, **options):
        self.stdout.write("Populating demo data...")

        # 1. Delivery Zones
        zone1, _ = DeliveryZone.objects.get_or_create(
            name="Downtown & Financial",
            defaults={"fee": Decimal("3.50"), "is_active": True},
        )
        zone2, _ = DeliveryZone.objects.get_or_create(
            name="North Suburbs",
            defaults={"fee": Decimal("5.00"), "is_active": True},
        )
        zone3, _ = DeliveryZone.objects.get_or_create(
            name="University Campus",
            defaults={"fee": Decimal("2.00"), "is_active": True},
        )

        # 2. Couriers
        courier_users = [
            ("courier_alex", "alex@freshroute.com", "+996555110001", "Alex Rivera", True),
            ("courier_sarah", "sarah@freshroute.com", "+996555110002", "Sarah Connor", True),
            ("courier_david", "david@freshroute.com", "+996555110003", "David Kim", True),
            ("courier_elena", "elena@freshroute.com", "+996555110004", "Elena Rostova", False),
        ]
        couriers = []
        for uname, email, phone, full_name, avail in courier_users:
            u, _ = User.objects.get_or_create(
                username=uname,
                defaults={"email": email, "role": User.Role.COURIER, "first_name": full_name.split()[0], "last_name": full_name.split()[1]},
            )
            u.set_password("pass1234")
            u.save()
            c, _ = Courier.objects.get_or_create(
                user=u,
                defaults={"phone": phone, "is_available": avail},
            )
            c.is_available = avail
            c.save()
            couriers.append(c)

        # 3. Restaurant Owners & Restaurants
        owner1, _ = User.objects.get_or_create(
            username="owner_marco",
            defaults={"email": "marco@artisanburger.com", "role": User.Role.OWNER, "first_name": "Marco", "last_name": "Rossi"},
        )
        owner1.set_password("pass1234")
        owner1.save()

        rest1, _ = Restaurant.objects.get_or_create(
            name="Artisan Burger & Greens",
            defaults={
                "owner": owner1,
                "phone": "+996555220001",
                "address": "42 Main Avenue, Downtown",
                "description": "Gourmet smash burgers, loaded fries, and organic salads.",
                "is_approved": True,
                "is_active": True,
            },
        )

        owner2, _ = User.objects.get_or_create(
            username="owner_kenji",
            defaults={"email": "kenji@tokyoramen.com", "role": User.Role.OWNER, "first_name": "Kenji", "last_name": "Sato"},
        )
        owner2.set_password("pass1234")
        owner2.save()

        rest2, _ = Restaurant.objects.get_or_create(
            name="Tokyo Ramen Lab",
            defaults={
                "owner": owner2,
                "phone": "+996555220002",
                "address": "15 Sakura Street, Suite 3",
                "description": "Authentic 24-hr simmered tonkotsu broth and handmade noodles.",
                "is_approved": False,  # Pending approval!
                "is_active": True,
            },
        )

        owner3, _ = User.objects.get_or_create(
            username="owner_amira",
            defaults={"email": "amira@beirutbistro.com", "role": User.Role.OWNER, "first_name": "Amira", "last_name": "Mansour"},
        )
        owner3.set_password("pass1234")
        owner3.save()

        rest3, _ = Restaurant.objects.get_or_create(
            name="Beirut Shawarma & Mezze",
            defaults={
                "owner": owner3,
                "phone": "+996555220003",
                "address": "88 Cedar Blvd",
                "description": "Wood-fired rotisserie shawarma and freshly whipped hummus.",
                "is_approved": False,  # Pending approval!
                "is_active": True,
            },
        )

        # 4. Food Products
        cat_burgers, _ = FoodCategory.objects.get_or_create(restaurant=rest1, name="Burgers")
        cat_sides, _ = FoodCategory.objects.get_or_create(restaurant=rest1, name="Sides & Drinks")

        prod_truffle, _ = FoodProduct.objects.get_or_create(
            restaurant=rest1,
            name="Truffle Mushroom Burger",
            defaults={"category": cat_burgers, "price": Decimal("14.50"), "is_vegetarian": True, "is_available": True},
        )
        prod_bacon, _ = FoodProduct.objects.get_or_create(
            restaurant=rest1,
            name="Smoked Bacon Double Stack",
            defaults={"category": cat_burgers, "price": Decimal("16.00"), "is_vegetarian": False, "is_available": True},
        )
        prod_fries, _ = FoodProduct.objects.get_or_create(
            restaurant=rest1,
            name="Crispy Rosemary Truffle Fries",
            defaults={"category": cat_sides, "price": Decimal("5.50"), "is_vegetarian": True, "is_available": True},
        )

        # 5. Customers
        cust_user1, _ = User.objects.get_or_create(
            username="customer_emily",
            defaults={"email": "emily@example.com", "role": User.Role.CUSTOMER, "first_name": "Emily", "last_name": "Watson"},
        )
        cust_user1.set_password("pass1234")
        cust_user1.save()
        cust1, _ = Customer.objects.get_or_create(user=cust_user1, defaults={"phone": "+996555330001"})

        cust_user2, _ = User.objects.get_or_create(
            username="customer_liam",
            defaults={"email": "liam@example.com", "role": User.Role.CUSTOMER, "first_name": "Liam", "last_name": "Chen"},
        )
        cust_user2.set_password("pass1234")
        cust_user2.save()
        cust2, _ = Customer.objects.get_or_create(user=cust_user2, defaults={"phone": "+996555330002"})

        # 6. Active Orders in different states
        now = timezone.now()

        # Order 1: OUT_FOR_DELIVERY
        o1, created1 = Order.objects.get_or_create(
            customer=cust1,
            restaurant=rest1,
            subtotal=Decimal("36.00"),
            defaults={
                "courier": couriers[0],
                "status": Order.Status.OUT_FOR_DELIVERY,
                "delivery_address": "Flat 4B, 120 Greenview Lane, Downtown",
                "payment_method": Order.PaymentMethod.STRIPE,
                "payment_status": Order.PaymentStatus.PAID,
                "delivery_fee": Decimal("3.50"),
                "discount_amount": Decimal("0.00"),
                "total_amount": Decimal("39.50"),
                "accepted_at": now - timedelta(minutes=25),
            },
        )
        if created1:
            OrderItem.objects.create(order=o1, product=prod_bacon, quantity=2, unit_price=Decimal("16.00"))
            OrderItem.objects.create(order=o1, product=prod_fries, quantity=1, unit_price=Decimal("4.00"))

        # Order 2: PREPARING
        o2, created2 = Order.objects.get_or_create(
            customer=cust2,
            restaurant=rest1,
            subtotal=Decimal("20.00"),
            defaults={
                "courier": couriers[1],
                "status": Order.Status.PREPARING,
                "delivery_address": "Building 7, Campus North, Dorm 12",
                "payment_method": Order.PaymentMethod.COD,
                "payment_status": Order.PaymentStatus.UNPAID,
                "delivery_fee": Decimal("2.00"),
                "discount_amount": Decimal("0.00"),
                "total_amount": Decimal("22.00"),
                "accepted_at": now - timedelta(minutes=10),
            },
        )
        if created2:
            OrderItem.objects.create(order=o2, product=prod_truffle, quantity=1, unit_price=Decimal("14.50"))
            OrderItem.objects.create(order=o2, product=prod_fries, quantity=1, unit_price=Decimal("5.50"))

        # Order 3: READY (Awaiting courier)
        o3, created3 = Order.objects.get_or_create(
            customer=cust1,
            restaurant=rest1,
            subtotal=Decimal("32.00"),
            defaults={
                "courier": None,  # Needs dispatch!
                "status": Order.Status.READY,
                "delivery_address": "Floor 9, Financial Tower 2",
                "payment_method": Order.PaymentMethod.STRIPE,
                "payment_status": Order.PaymentStatus.PAID,
                "delivery_fee": Decimal("3.50"),
                "discount_amount": Decimal("5.00"),
                "total_amount": Decimal("30.50"),
                "accepted_at": now - timedelta(minutes=18),
            },
        )
        if created3:
            OrderItem.objects.create(order=o3, product=prod_bacon, quantity=2, unit_price=Decimal("16.00"))

        # 7. Complaints
        Complaint.objects.get_or_create(
            order=o1,
            defaults={
                "description": "Courier took wrong turn; order delay over 20 minutes and drink was spilled.",
                "status": Complaint.Status.OPEN,
            },
        )
        Complaint.objects.get_or_create(
            order=o2,
            defaults={
                "description": "Customer requested no pickles on Bacon Stack but pickles were included.",
                "status": Complaint.Status.IN_PROGRESS,
                "admin_notes": "Contacted kitchen manager; issuing $5 refund credit.",
            },
        )

        self.stdout.write(self.style.SUCCESS("Demo data populated successfully!"))
