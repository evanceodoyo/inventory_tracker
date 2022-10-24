from django.contrib import admin
from . models import (Category, Product, ProductSpecification, 
Order, OrderItem, ProductSupplier, ShippingAddress, Payment)


@property
def short_name(self):
    return self.name if len(self.name) < 35 else f'{self.name[:33]}..'

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'quantity', 'reorder_level', 'old_price', 'price', 'created']
    prepopulated_fields = {'slug': ('name',)}
    

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'created']
    prepopulated_fields = {'slug': ('title', )}

class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'customer', 'amount', 'created', 'status']

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['item', 'quantity', 'order']

class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ['customer', 'county', 'street', 'apartment', 'phone']

class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order', 'customer', 'amount', 'phone', 'payment_time']

class ProductSupplierAdmin(admin.ModelAdmin):
    list_display = ['supplier', 'product']

admin.site.register(Product, ProductAdmin)
admin.site.register(Category,CategoryAdmin)
admin.site.register(ProductSpecification)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(ShippingAddress, ShippingAddressAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(ProductSupplier, ProductSupplierAdmin)
