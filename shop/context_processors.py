from django.conf import settings
from dashboard.models import Notification
from accounts.models import Supplier


def global_context_renderer(request):
    context = {}
    notifications = Notification.objects.select_related("product", "supplier").all()
    if request.user.is_authenticated and request.user.user_type == "SUPPLIER":
        fn = notifications.filter(supplier=Supplier.objects.get(name=request.user))
        context["fn"] = fn
        context["s_unread_ntfs"] = fn.filter(unread=True).count()
    context.update(
        {
            "page_title": settings.PAGE_TITLE,
            "site_name": settings.SITE_NAME,
            "site_icon": "M",
            "notifications": notifications[:5],
            "unread_ntfs": notifications.filter(unread=True).count(),
        }
    )
    return context
