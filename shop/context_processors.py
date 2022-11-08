from django.conf import settings
from dashboard.models import Notification


def global_context_renderer(request):
    return {
        "page_title": settings.PAGE_TITLE,
        "site_name": settings.SITE_NAME,
        "site_icon": "M",
        "notifications": Notification.objects.select_related("product")[:5],
        "unread_ntfs": Notification.objects.filter(unread=True).count(),
    }
