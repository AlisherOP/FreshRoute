from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0003_coupon_review_and_more"),
        ("restaurants", "0003_openinghour_and_more"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="foodproduct",
            name="unique_product_restaurant_pair",
        ),
    ]
