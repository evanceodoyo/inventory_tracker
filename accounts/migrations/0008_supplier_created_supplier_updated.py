# Generated by Django 4.1.2 on 2022-10-31 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0007_alter_user_user_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="supplier",
            name="created",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name="supplier",
            name="updated",
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
