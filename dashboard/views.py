from django.shortcuts import render
from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator, InvalidPage
from shop.models import Product


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
