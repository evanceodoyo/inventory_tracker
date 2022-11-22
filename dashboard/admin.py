from django.contrib import admin
from .models import (
    PurchaseCartProduct,
    PurchaseOrder,
    PurchaseOrderPayment,
    PurchaseOrderProduct,
    Notification,
    AccountBalance
)


class NotificationAdmin(admin.ModelAdmin):
    list_display = ["product", "message", "created", "unread"]


admin.site.register(PurchaseCartProduct)
admin.site.register(PurchaseOrder)
admin.site.register(PurchaseOrderProduct)
admin.site.register(PurchaseOrderPayment)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(AccountBalance)
