from django.shortcuts import get_object_or_404, render, redirect
from .models import Category, Payment, Product, ShippingAddress, Order, OrderItem
from django.contrib import messages
from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator, InvalidPage
from django.contrib.auth.decorators import login_required
from django.db import transaction
from payments.views import lipa_na_mpesa_online


def home(request):
    try:
        categories = Category.objects.all()
        page = request.GET.get("page")
        if category := request.GET.get("category"):
            products = Product.objects.filter(
                categories__slug__in=[category], status=True
            )
        else:
            products = Product.objects.filter(status=True)
        paginator = Paginator(products, 15)
        try:
            products = paginator.page(page)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)
        except (PageNotAnInteger, InvalidPage):
            products = paginator.page(1)

        return render(
            request,
            "products.html",
            {"page_title": "Shop", "products": products, "categories": categories},
        )
    except Exception as e:
        raise e


def product_detail(request, product_slug):
    """
    Get the product and related products i.e
    the products in the same category/ies.
    """
    product = get_object_or_404(Product, slug=product_slug)
    categories = Category.objects.all()
    related_product_ids = product.categories.values_list("id", flat=True)
    related_products = (
        Product.objects.filter(status=True)
        .filter(categories__in=related_product_ids)
        .exclude(id=product.id)
        .distinct()
    )

    return render(
        request,
        "product.html",
        {
            "page_title": product.name,
            "product": product,
            "categories": categories,
            "related_products": related_products,
        },
    )


def add_to_cart(request):
    if request.method == "POST":
        product_id = request.POST.get("product")
        product = Product.objects.get(id=product_id)
        cart = request.session.get("cart")
        remove = request.POST.get("remove")
        add_msg = "Item added to cart successfully"
        if cart:
            if quantity := cart.get(product_id):
                update_msg = "Item quantity updated successfully"
                if remove:
                    if quantity <= 1:
                        cart.pop(product_id)
                        messages.success(request, "Item removed from cart successfully")
                    else:
                        cart[product_id] = quantity - 1
                        messages.success(request, update_msg)
                else:
                    cart[product_id] = quantity + 1
                    messages.success(request, update_msg)
            else:
                cart[product_id] = 1
                messages.success(request, add_msg)
        else:
            cart = {product_id: 1}
            messages.success(request, add_msg)

        request.session["cart"] = cart
    return redirect(product)


def cart(request):
    """
    Get the cart ids from session and use the
    ids to get the items from the database.
    """
    try:
        cart = request.session.get("cart")
        cart_items = Product.get_products_by_ids(list(cart.keys()))
        context = {"page_title": "Cart", "cart_items": cart_items}
        if item_id := request.GET.get("item_id"):
            cart.pop(str(item_id))
            request.session.save()
            messages.success(request, "Item removed from cart successfully")
            return redirect("cart")

        return render(request, "shopping-cart.html", context)
    except Exception:
        return render(request, "shopping-cart.html")


def clear_cart(request):
    """
    Clear the cart session data.
    """
    request.session["cart"] = {}
    messages.success(request, "Cart cleared successfully")
    return redirect("cart")


@login_required
def checkout(request):
    if not request.session.get("cart"):
        messages.info(request, "Please add items to your cart")
        return redirect("home")
    context = {"page_title": "Cart"}
    cart = request.session.get("cart")
    user = request.user
    if user.shipping_address:
        context["shipping_address"] = user.shipping_address.first()
    order_items = Product.get_products_by_ids(list(cart.keys()))
    context["order_items"] = order_items
    if request.method == "POST":
        county = request.POST.get("county")
        street = request.POST.get("street")
        apartment = request.POST.get("apartment")
        phone = request.POST.get("phone")

        try:
            """
            If user already has a shipping address, update it.
            """
            shipping_address = ShippingAddress.objects.get(customer=user)
            context["shipping_address"] = shipping_address
            shipping_address.county = county
            shipping_address.street = street
            shipping_address.apartment = apartment
            shipping_address.phone = phone
            shipping_address.customer = user
            shipping_address.save()
            messages.info(request, "Shipping address updated successfully")
            return redirect("checkout")
        except ShippingAddress.DoesNotExist:
            """
            If no shipping address associated with the user,
            create and save a new one.
            """
            ShippingAddress.objects.create(
                county=county,
                street=street,
                apartment=apartment,
                phone=phone,
                customer=user,
            )
            messages.success(request, "Shipping address saved successfully")
            return redirect("checkout")

    return render(request, "checkout.html", context)


def get_order_total(cart):
    ids = cart.keys()
    total = 0
    for id in ids:
        item_qnty = cart.get(id)
        item = Product.objects.get(id=int(id))
        total += item_qnty * item.price
    return total


@login_required
@transaction.atomic
def payment(request):
    if not request.session.get("cart"):
        messages.info(request, "Please add items to your cart")
        return redirect("home")
    if request.method == "POST":
        phone = request.POST.get("phone")
        user = request.user
        cart = request.session.get("cart")
        order_items = Product.get_products_by_ids(list(cart.keys()))

        order = Order(
            customer=user,
            amount=get_order_total(cart),
            shipping_address=user.shipping_address.first(),
        )
        order.save()

        # use select_for_update() to obtain a lock on the items
        # and avoiding race conditions.
        for item in order_items.select_for_update():
            order_item = OrderItem.objects.create(
                order=order, item=item, quantity=cart.get(str(item.id))
            )
            item.quantity -= order_item.quantity
            if item.quantity < 1:
                item.status = False
            item.save()
            item.refresh_from_db()

        lipa_na_mpesa_online(request, phone=phone, amount=order.amount)
        Payment.objects.create(
            order=order, customer=user, phone=phone, amount=order.amount
        )

        request.session["cart"] = {}
        return redirect("home")
