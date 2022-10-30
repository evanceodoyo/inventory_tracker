from django.contrib import admin
from .models import (
    PurchaseCartProduct,
    PurchaseOrder,
    PurchaseOrderProduct,
    Notification,
)


class NotificationAdmin(admin.ModelAdmin):
    list_display = ["product", "message", "created", "is_sent"]


admin.site.register(PurchaseCartProduct)
admin.site.register(PurchaseOrder)
admin.site.register(PurchaseOrderProduct)
admin.site.register(Notification, NotificationAdmin)
