from django.urls import path
from . views import dashboard, edit_product

urlpatterns = [
    path('', dashboard, name="dashboard" ),
    path('products/edit/<slug:product_slug>/', edit_product, name="edit_product" ),
]