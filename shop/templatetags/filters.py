from django import template
from shop.models import OrderItem
from django.db.models import Sum

register = template.Library()


@register.filter(name='is_in_cart')
def is_in_cart(product, cart):
    ids = cart.keys()
    return any(int(id) == product.id for id in ids)

@register.filter(name='quantity_in_cart')
def quantity_in_cart(product, cart):
    ids = cart.keys()
    return next((cart.get(id) for id in ids if int(id) == product.id), 0)

@register.filter(name='total_price')
def total_price(product, cart):
    return product.price * quantity_in_cart(product, cart)

@register.filter(name='grand_product_total')
def grand_product_total(products, cart):    # sourcery skip: avoid-builtin-shadow
    sum = 0
    for product in products:
        sum += total_price(product, cart)
    return sum

@register.filter(name='order_item_total')
def order_item_total(quantity, price):
    return quantity * price

@register.filter(name="total_cart_items")
def total_cart_items(values):
    return sum(values)

@register.filter(name="quantity_sold")
def quantity_sold(product):
    item = OrderItem.objects.filter(item_id=product.id).aggregate(qty_sold=Sum('quantity'))
    # print(item)
    return item['qty_sold']

# @register.filter(name="send_notification")
# def send_notification(request, product):
#     if product.quantity <= product.reorder_level:
#         sender = settings.EMAIL_HOST_USER
#         recipient = 'admin@gmail.com'
#         message = f'{product.name} is soon running out of stock, reorder now'
#         notify.send(sender, recipient=recipient, verb='Stock Level notification', description=message)
#     else:
#         pass
    
