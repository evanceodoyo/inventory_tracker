from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator, InvalidPage
from shop.models import Category, Product, ProductSpecification
from django.contrib.auth.decorators import login_required
from accounts.decorators import retailer_required
from django.contrib import messages


@login_required
@retailer_required
def dashboard(request):
    try:
        products = Product.objects.prefetch_related("items_sold").order_by('quantity')
        page = request.GET.get('page')
        paginator = Paginator(products, 20)

        try:
            products = paginator.page(page)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)
        except (PageNotAnInteger, InvalidPage):
            products = paginator.page(1)
        return render(request, "retail-dashboard.html", {"page_title": "Retail Dashboard", "products":products})
    except Exception as e:
        raise e

def edit_product(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    categories = Category.objects.all()[:5]
    specifications = ProductSpecification.objects.all()
    if request.method == 'POST':
        name = request.POST.get("name")
        description = request.POST.get("description")
        categories =request.POST.getlist("categories")
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
        product.status = status
        if specifications:
            product.specifications.set(specifications)
        if categories:
            product.categories.set(categories)
        product.save()
        messages.success(request, "Product updated successfully.")
        return redirect(product)
        # return redirect('edit_product', product_slug=product.slug)

    return render(request, 'product-edit.html', {"page_title": "Product Edit", "product": product, "categories": categories, "specifications": specifications})
