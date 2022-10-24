from django.conf import settings

def global_context_renderer(request):
    return {
        "page_title": settings.PAGE_TITLE,
        "site_name": settings.SITE_NAME,
        "site_icon": 'M',
    }