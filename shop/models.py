from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.db.models.signals import pre_save
from django.db.models import F
from accounts.models import Supplier
from .utils import unique_order_id_generator


class TimeStampedModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(TimeStampedModel):
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=50)
    description = models.CharField(max_length=300, blank=True, null=True)

    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'Categories'
        ordering = ['created']

    def __str__(self):
        return self.title


class Product(TimeStampedModel):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    slug = models.SlugField(max_length=50)
    categories = models.ManyToManyField(Category, related_name="products")
    image = models.ImageField(upload_to='products/images')
    sku = models.CharField(max_length=100)
    old_price = models.FloatField(default=0.0)
    price = models.FloatField()
    quantity = models.PositiveIntegerField(default=1)
    reorder_level = models.PositiveIntegerField(default=6)
    status = models.BooleanField("In stock", default=True)
    specifications = models.ManyToManyField("ProductSpecification", max_length=4)

    class Meta:
        db_table = 'products'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'product_slug': self.slug})

    def discount(self):
        if self.old_price > self.price:
            return ((self.old_price - self.price) / self.old_price * 100)

    def get_products_by_ids(product_ids): # sourcery skip
        return Product.objects.filter(id__in=product_ids)

# def update_product_status(sender, instance, *args, **kwargs): # TO DO ; MOve to celery
#     """
#     Update the product status on every update/save.
#     """
#     if instance.status and  int(instance.quantity) < 1:
#         instance.status = False
#     else:
#         instance.status = True
        
# pre_save.connect(update_product_status, sender=Product)


class ProductSpecification(models.Model):
    title = models.CharField("Product Specification/Feature", max_length=80, unique=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'product_specifications'
        ordering = ['title']

class ShippingAddress(TimeStampedModel):
    customer = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='shipping_address')
    county = models.CharField(max_length=50, blank=True, null=True)
    street = models.CharField(max_length=80)
    apartment = models.CharField(max_length=80)
    phone = models.CharField(max_length=13)

    class Meta:
        db_table = "shipping_address"

    def __str__(self):
        return f'Shipping address for {self.customer}.'


class Order(TimeStampedModel):
    ORDER_STATUS = (
        ("PENDING", "Pending"),
        ("AWAITING SHIPMENT", "Awaiting Shipment"),
        ("SHIPPED", "Shipped"),
        ("DELIVERED", "Delivered"),
        ("COMPLETED", "Completed"),
        ("DISPUTED", "Disputed")
    )
    order_id = models.CharField(max_length=10, unique=True)
    customer = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, related_name="orders", null=True)
    amount = models.FloatField()
    status = models.CharField(choices=ORDER_STATUS, default="Pending", max_length=20)
    shipping_address = models.ForeignKey(ShippingAddress, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = "orders"

    def __str__(self):
        return f'Order #{self.order_id}'


def create_order_id(sender, instance, *args, **kwargs):
    if not instance.order_id:
        instance.order_id = unique_order_id_generator(instance)

pre_save.connect(create_order_id, sender=Order)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    item = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name="items_sold")
    quantity = models.PositiveIntegerField(default=1)
    date_ordered = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "order_items"

    def __str__(self):
        return f'{self.item} in {self.order}'


class Payment(models.Model):
    customer = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True)
    phone = models.CharField(max_length=13)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    payment_time = models.DateTimeField(auto_now_add=True)
    amount = models.FloatField()

    class Meta:
        db_table = "payments"

    def __str__(self):
        return f"Payment for {self.order}: Amount = {self.amount}"


class ProductSupplier(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="suppliers")
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='products')

    class Meta:
        db_table = 'product_suppliers'

    def __str__(self):
        return self.supplier.company_name