# Generated by Django 4.1.2 on 2022-10-19 23:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0009_orderitem_quantity_product_quantity_sold"),
    ]

    operations = [
        migrations.AlterField(
            model_name="orderitem",
            name="item",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="items_sold",
                to="shop.product",
            ),
        ),
        migrations.AlterField(
            model_name="orderitem",
            name="order",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="order_items",
                to="shop.order",
            ),
        ),
    ]
