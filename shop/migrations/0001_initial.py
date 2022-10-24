# Generated by Django 4.1.2 on 2022-10-14 14:51

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ProductSpecification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=80, unique=True, verbose_name='Product Specification/Feature')),
            ],
            options={
                'db_table': 'product_specifications',
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=100)),
                ('description', models.CharField(blank=True, max_length=300, null=True)),
            ],
            options={
                'db_table': 'tags',
                'ordering': ['created'],
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(max_length=500)),
                ('slug', models.SlugField()),
                ('image', models.ImageField(upload_to='products/images')),
                ('sku', models.CharField(max_length=100)),
                ('old_price', models.FloatField(default=0.0)),
                ('price', models.FloatField()),
                ('reorder_level', models.PositiveIntegerField(default=6)),
                ('status', models.BooleanField(default=True, verbose_name='In stock')),
                ('specifications', models.ManyToManyField(max_length=4, to='shop.productspecification')),
                ('tags', models.ManyToManyField(related_name='products', to='shop.tag')),
            ],
            options={
                'db_table': 'products',
            },
        ),
    ]
