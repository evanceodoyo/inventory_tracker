from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator, InvalidPage
from shop.models import Category, Order, Product, ProductSpecification
from accounts.decorators import retailer_required
from django.contrib import messages
from accounts.models import Supplier
from django.db import transaction
from .models import (
    Notification,
    PurchaseCartProduct,
    PurchaseOrder,
    PurchaseOrderProduct,
    PurchaseOrderPayment,
)

from django.db.models import F, Sum,Count
from django.db.models.functions import ExtractDay, ExtractMonth, ExtractYear


@retailer_required
def dashboard(request):
    try:
        products = Product.objects.prefetch_related("items_sold").order_by("quantity")
        balance = Order.objects.aggregate(bal=Sum("amount"))
        # Get the total sales per day for the last 7 days.
        sales = Order.objects.annotate(day=ExtractDay('created'), month=ExtractMonth('created'), year=ExtractYear('created')).values('order_id', 'month', 'day').annotate(total=Sum('amount')).order_by('created')
        print(sales)
        total_sales = []
        dates = []
        for s in sales:
            dates.append(f"{s['month']}/{s['day']}")
            total_sales.append(s["total"])
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
            {"page_title": "Retail Dashboard", "products": products, "balance": balance['bal'], "dates": dates, "total_sales": total_sales},
        )
    except Exception as e:
        raise e


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


@retailer_required
def delete_product(request, product_slug):
    if request.method == "POST":
        product = get_object_or_404(Product, slug=product_slug)
        product.delete()
        messages.info(request, f"{product.name} deleted successfully.")
        return redirect("dashboard")
    return redirect("dashboard")


@retailer_required
def activate_deactivate_product(request, product_slug):
    if request.method == "POST":
        product = get_object_or_404(Product, slug=product_slug)
        product.status = product.status != True
        product.save()
        messages.success(request, "Product status updated successfully.")
        return redirect("dashboard")
    return redirect("dashboard")


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
    suppliers = Supplier.objects.all()
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
            "suppliers": suppliers,
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


@transaction.atomic
def place_purchase_order(request):
    if cart_products := PurchaseCartProduct.objects.select_related("product"):
        total = sum((p.quantity * p.product.price) for p in cart_products)
        if request.method == "POST":
            order_notes = request.POST.get("order_notes")
            supplier = request.POST.get("supplier")
            # pay_agreement = request.POST.get('pay_agreement')
            purchase_order = PurchaseOrder(
                user=request.user,
                amount=total,
                supplier=supplier,
                order_notes=order_notes,
            )
            purchase_order.save()
            PurchaseOrderPayment.objects.create(
                purchase_order=purchase_order, amount=purchase_order.amount
            )

            for p in cart_products.select_for_update():
                PurchaseOrderProduct.objects.create(
                    supplier=supplier,
                    purchase_order=purchase_order,
                    product=p.product,
                    quantity=p.quantity,
                )
                p.delete()
            messages.success(request, "Purchase order placed successfully.")
    else:
        messages.success(request, "No products in cart to reorder")

    return redirect("dashboard")


def notifications(request):
    notifications = Notification.objects.select_related("product").order_by(
        "-created", "-unread"
    )
    products = Product.objects.filter(notification_sent=False).order_by("quantity")[:15]
    if request.method == "POST":
        notification = get_object_or_404(
            Notification, id=request.POST.get("notification_id")
        )
        if "read" in request.POST:
            notification.unread = False
            notification.save()
            messages.success(request, "Notification marked as read.")
            return redirect("notifications")
        if "delete" in request.POST:
            notification.delete()
            messages.info(request, "Notification deleted successfully.")
            return redirect("notifications")

    return render(
        request,
        "notifications.html",
        {
            "page_title": "Notifications",
            "notifications": notifications,
            "products": products,
        },
    )
