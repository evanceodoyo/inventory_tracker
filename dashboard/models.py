from email.policy import default
from django.db import models
from accounts.models import Supplier
from shop.models import Product, TimeStampedModel
from django.contrib.auth import get_user_model
from django.db.models.signals import pre_save
from shop.utils import unique_order_id_generator


class PurchaseOrder(TimeStampedModel):
    order_id = models.CharField(max_length=10, unique=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True)
    amount = models.FloatField()
    order_notes = models.TextField(default="")
    # is_paid = models.BooleanField(default=False)

    class Meta:
        db_table = "purchase_orders"

    def __str__(self):
        return f"Purchase Order #{self.order_id}"


def create_purchase_order_id(sender, instance, *args, **kwargs):
    if not instance.order_id:
        instance.order_id = unique_order_id_generator(instance)


pre_save.connect(create_purchase_order_id, sender=PurchaseOrder)


class PurchaseOrderProduct(TimeStampedModel):
    purchase_order = models.ForeignKey(
        PurchaseOrder, on_delete=models.CASCADE, related_name="order_items"
    )
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True, related_name="purchases"
    )
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()

    class Meta:
        db_table = "purchase_order_items"

    def __str__(self):
        return f"{self.product.name} in {self.purchase_order}"

    def sub_total(self):
        return self.product.price * self.quantity


class PurchaseOrderPayment(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE)
    amount = models.FloatField()
    transaction_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "purchase_order_payments"

    def __str__(self):
        return f"{self.purchase_order}: Amount {self.amount}"


class PurchaseCartProduct(TimeStampedModel):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = "purchase_cart_items"

    def __str__(self):
        return f"{self.product.name}: {self.quantity}"

    def sub_total(self):
        return self.quantity * self.product.price


class Notification(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="notifications"
    )
    message = models.CharField(max_length=400)
    unread = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "notifications"
        ordering = ["-created"]

    def __str__(self):
        return f"{self.message} for {self.product.name}"
