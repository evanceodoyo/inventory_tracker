# Generated by Django 4.1.2 on 2022-10-31 09:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0008_rename_purchase_order_id_purchaseorder_order_id"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="notification",
            options={"ordering": ["-created"]},
        ),
        migrations.RemoveField(
            model_name="notification",
            name="is_sent",
        ),
    ]
