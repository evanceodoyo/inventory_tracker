from django.urls import path
from . views import (
    dashboard, delete_product, edit_product,
    activate_deactivate_product, add_to_reorder_cart, remove_from_cart, reorder
)

urlpatterns = [
    path('', dashboard, name="dashboard" ),
    path('products/edit/<slug:product_slug>/', edit_product, name="edit_product" ),
    path('products/delete/<slug:product_slug>/', delete_product, name="delete_product" ),
    path('products/activate-deactivate/<slug:product_slug>/', activate_deactivate_product, name="product_activate_deactivate" ),
    path('add-to-purchase-cart/', add_to_reorder_cart, name="add_to_reorder_cart"),
    path('reorder/', reorder, name='reorder'),
    path('remove-from-cart/', remove_from_cart, name='remove_from_cart'),
]