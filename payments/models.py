from django.db import models

from shop.models import Order


class MpesaPayment(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    description = models.TextField()
    type = models.TextField()
    reference = models.TextField()
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    organization_balance = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = "mpesa_payments"

    def __str__(self):
        return f"{self.first_name} {self.last_name}, Amount: {self.amount}"
