from django.urls import path
from .views import (
    clear_cart,
    home,
    payment,
    product_detail,
    add_to_cart,
    cart,
    checkout,
)

urlpatterns = [
    path("", home, name="home"),
    path("products/<slug:product_slug>/", product_detail, name="product_detail"),
    path("add_to_cart/", add_to_cart, name="add_to_cart"),
    path("shopping-cart/", cart, name="cart"),
    path("clear-cart/", clear_cart, name="clear_cart"),
    path("checkout/", checkout, name="checkout"),
    path("payment/", payment, name="payment"),
]
