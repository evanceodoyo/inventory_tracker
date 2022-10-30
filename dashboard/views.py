from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator, InvalidPage
from shop.models import Category, Order, Product, ProductSpecification
from django.contrib.auth.decorators import login_required
from accounts.decorators import retailer_required
from django.contrib import messages
from accounts.models import Supplier
from django.db.models import Sum
from .models import PurchaseCartProduct, PurchaseOrder, PurchaseOrderProduct

from django.db.models import F


@login_required
@retailer_required
def dashboard(request):
    try:
        products = Product.objects.prefetch_related("items_sold").order_by("quantity")
        page = request.GET.get("page")
        paginator = Paginator(products, 20)

        try:
            products = paginator.page(page)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)
        except (PageNotAnInteger, InvalidPage):
            products = paginator.page(1)
        return render(
            request,
            "retail-dashboard.html",
            {"page_title": "Retail Dashboard", "products": products},
        )
    except Exception as e:
        raise e


@login_required
@retailer_required
def edit_product(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    categories = Category.objects.all()[:5]
    specifications = ProductSpecification.objects.all()
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        categories = request.POST.getlist("categories")
        image = request.FILES.get("image", product.image)
        sku = request.POST.get("sku")
        old_price = request.POST.get("old_price")
        price = request.POST.get("price")
        quantity = request.POST.get("quantity")
        reorder_level = request.POST.get("reorder_level")
        status = request.POST.get("status")
        specifications = request.POST.getlist("specifications")

        product.name = name
        product.description = description
        product.image = image
        product.sku = sku
        product.old_price = old_price
        product.price = price
        product.reorder_level = reorder_level
        product.quantity = quantity
        product.status = bool(status)
        if specifications:
            product.specifications.set(specifications)
        if categories:
            product.categories.set(categories)
        product.save()
        messages.success(request, "Product updated successfully.")
        return redirect(product)

    return render(
        request,
        "product-edit.html",
        {
            "page_title": "Product Edit",
            "product": product,
            "categories": categories,
            "specifications": specifications,
        },
    )


@login_required
@retailer_required
def delete_product(request, product_slug):
    if request.method == "POST":
        product = get_object_or_404(Product, slug=product_slug)
        product.delete()
        messages.info(request, f"{product.name} deleted successfully.")
        return redirect("dashboard")
    return redirect("dashboard")


@login_required
@retailer_required
def activate_deactivate_product(request, product_slug):
    if request.method == "POST":
        product = get_object_or_404(Product, slug=product_slug)
        product.status = product.status != True
        product.save()
        messages.success(request, "Product status updated successfully.")
        return redirect("dashboard")
    return redirect("dashboard")


@login_required
@retailer_required
def add_to_reorder_cart(request):
    if request.method == "POST":
        product = get_object_or_404(Product, id=request.POST.get("product_id"))
        if not PurchaseCartProduct.objects.filter(product=product).exists():
            prd = PurchaseCartProduct.objects.create(user=request.user, product=product)
            messages.success(
                request, f"{product.name} added to purchase cart successfully."
            )

            return redirect("dashboard")
    return redirect("dashboard")


def recommend_suppliers(cart_products):
    rms = cart_products.annotate()


def reorder(request):
    cart_products = PurchaseCartProduct.objects.select_related("product")
    balance = Order.objects.aggregate(bal=Sum("amount"))
    if request.method == "POST":
        cart_product = cart_products.get(id=int(request.POST["cart_product"]))
        if "remove" in request.POST:
            if cart_product.quantity == 1:
                cart_product.delete()
            else:
                cart_product.quantity = F("quantity") - 1
                cart_product.save()
                cart_product.refresh_from_db()
            return redirect("reorder")
        elif "add" in request.POST:
            cart_product.quantity = F("quantity") + 1
            cart_product.save()
            cart_product.refresh_from_db()
            return redirect("reorder")

    return render(
        request,
        "purchase-order.html",
        {
            "page_title": "Products Reorder",
            "cart_products": cart_products,
            "balance": balance["bal"],
        },
    )


def remove_from_cart(request):
    if request.method == "POST":
        product = get_object_or_404(PurchaseCartProduct, id=request.POST.get("product"))
        if product2 := get_object_or_404(
            PurchaseCartProduct, product_id=int(request.POST.get("product_id"))
        ):
            product2.delete()
            return redirect("dashboard")
        else:
            product.delete()
            return redirect("reorder")
    return redirect("reorder")
