from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator, InvalidPage
from shop.models import Category, Order, OrderItem, Product, ProductSpecification
from accounts.decorators import retailer_required, retailer_or_supplier_required
from django.contrib import messages
from accounts.models import Supplier
from django.db import transaction
from .models import (
    Notification,
    PurchaseCartProduct,
    PurchaseOrder,
    PurchaseOrderProduct,
    PurchaseOrderPayment,
    AccountBalance,
)
from shop.models import ProductSupplier
from django.db.models import F, Sum
from datetime import timedelta, datetime


@retailer_required
def dashboard(request):
    try:
        products = Product.objects.prefetch_related("items_sold").order_by("quantity")
        balance = AccountBalance.objects.get(id=1)

        # Get the total sales per day for the last 7 days
        # when sales were made. Assume days with zero sales.
        sales = Order.objects.values("date_created").annotate(total=Sum("amount"))[:7]
        total_sales = []
        dates = []
        for s in sales:
            total_sales.append(s["total"])
            dates.append(s["date_created"].strftime("%d/%m/%Y"))
        most_sold_products = (
            OrderItem.objects.filter(
                date_ordered__gte=datetime.now() - timedelta(days=7)
            )
            .values("item", "item__name")
            .annotate(qty=Sum("quantity"))
        )
        quantities = []
        prdcts = []
        for p in most_sold_products:
            prdcts.append(p["item__name"])
            quantities.append(p["qty"])
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
            {
                "page_title": "Retail Dashboard",
                "products": products,
                "balance": balance,
                "dates": dates,
                "total_sales": total_sales,
                "prdcts": prdcts,
                "quantities": quantities,
            },
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
            PurchaseCartProduct.objects.create(user=request.user, product=product)
            messages.success(
                request, f"{product.name} added to purchase cart successfully."
            )

            return redirect("dashboard")
    return redirect("dashboard")


def recommend_suppliers(cart_products, suppliers):
    """
    Recommend a supplier only if all the products in
    cart are supplied by the supplier.
    """
    cart_products_ids = cart_products.values_list("product_id", flat=True).distinct()
    return [
        s
        for s in suppliers
        if all(
            id in s.products.values_list("product_id", flat=True)
            for id in cart_products_ids
        )
    ]


@retailer_required
def reorder(request):
    cart_products = PurchaseCartProduct.objects.select_related("product")
    suppliers = Supplier.objects.all()
    balance = AccountBalance.objects.get(id=1)

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
            "recommended_suppliers": recommend_suppliers(cart_products, suppliers),
            "balance": balance,
        },
    )


@retailer_required
def remove_from_cart(request):
    if request.method == "POST":
        if p_id := request.POST.get("product"):
            cart_product = get_object_or_404(PurchaseCartProduct, id=p_id)
            cart_product.delete()
            return redirect("reorder")
        elif prdct_id := request.POST.get("product_id"):
            cart_product2 = get_object_or_404(PurchaseCartProduct, product_id=prdct_id)
            cart_product2.delete()
            return redirect("dashboard")

    return redirect("reorder")


@retailer_required
@transaction.atomic
def place_purchase_order(request):
    if cart_products := PurchaseCartProduct.objects.select_related("product"):
        total = sum((p.quantity * p.product.price) for p in cart_products)
        if request.method == "POST":
            order_notes = request.POST.get("order_notes")
            supplier = get_object_or_404(Supplier, id=request.POST.get("supplier"))
            # pay_agreement = request.POST.get('pay_agreement')
            bal = AccountBalance.objects.get(id=1)
            purchase_order = PurchaseOrder(
                user=request.user,
                amount=total,
                supplier=supplier,
                order_notes=order_notes,
            )
            if bal.balance < purchase_order.amount:
                messages.info(request, "Account balance too low. Order not placed.")
            else:
                purchase_order.save()
                PurchaseOrderPayment.objects.create(
                    purchase_order=purchase_order, amount=purchase_order.amount
                )
                bal.balance = F("balance") - purchase_order.amount
                bal.save()

                for p in cart_products.select_for_update():
                    PurchaseOrderProduct.objects.create(
                        supplier=supplier,
                        purchase_order=purchase_order,
                        product=p.product,
                        quantity=p.quantity,
                    )
                    # Adjust the product quantity to
                    # simulate product delivery
                    prdct = Product.objects.get(pk=p.product_id)
                    prdct.quantity = p.quantity
                    prdct.save()
                    p.delete()
                messages.success(request, "Purchase order placed successfully.")
            return redirect("reorder")
    else:
        messages.success(request, "No products in cart to reorder")

    return redirect("dashboard")


@retailer_or_supplier_required
def notifications(request):
    context = {}
    notifications = Notification.objects.select_related("product", "supplier").order_by(
        "-created", "-unread"
    )
    try:
        filtered_notifications = notifications.filter(
            supplier=Supplier.objects.get(name=request.user)
        )
        context["filtered_notifications"] = filtered_notifications
    except Supplier.DoesNotExist:
        pass
    products = Product.objects.filter(notification_sent=False).order_by("quantity")[:15]
    suppliers = (
        ProductSupplier.objects.select_related("supplier")
        .values("supplier__company_name")
        .order_by("date_signed")
        .distinct()[:8]
    )
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
    context.update(
        {
            "page_title": "Notifications",
            "notifications": notifications,
            "products": products,
            "suppliers": suppliers,
        },
    )
    return render(request, "notifications.html", context)


def suppliers(request):
    """
    List suppliers who have updated their
    profiles to supply certain products.
    """
    suppliers_ids = ProductSupplier.objects.values_list(
        "supplier_id", flat=True
    ).distinct()
    suppliers = Supplier.objects.select_related("name").filter(id__in=suppliers_ids)
    return render(request, "supplier-list.html", {"suppliers": suppliers})
