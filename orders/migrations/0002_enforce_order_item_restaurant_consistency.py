from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [

        # Ensure the order and order item belong to the same restaurant.
        migrations.RunSQL(
            sql="""
                ALTER TABLE order_items
                ADD CONSTRAINT order_item_order_restaurant_fk
                FOREIGN KEY (order_id, restaurant_id)
                REFERENCES orders (order_id, restaurant_id)
                ON DELETE CASCADE;
            """,
            reverse_sql="""
                ALTER TABLE order_items
                DROP CONSTRAINT order_item_order_restaurant_fk;
            """,
        ),

        # Ensure the product and order item belong to the same restaurant.
        migrations.RunSQL(
            sql="""
                ALTER TABLE order_items
                ADD CONSTRAINT order_item_product_restaurant_fk
                FOREIGN KEY (product_id, restaurant_id)
                REFERENCES food_products (product_id, restaurant_id)
                ON DELETE RESTRICT;
            """,
            reverse_sql="""
                ALTER TABLE order_items
                DROP CONSTRAINT order_item_product_restaurant_fk;
            """,
        ),

    ]