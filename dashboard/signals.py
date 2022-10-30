from shop.models import Product
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings

from .models import Notification


@receiver(post_save, sender=Product)
def create_notification(sender, instance, **kwargs):
    if instance.quantity <= instance.reorder_level:
        """
        Create notification and send email when the products
        levels is equal or is below the reorder level.
        """
        msg = f'"<a href="{instance.get_absolute_url()}">{instance.name}" </a> is almost running out of stock. Reorder to avoid running out of stock'
        Notification.objects.create(
            product=instance,
            message = msg,
        )
        send_mail(
            'Product Stock Levels',
            msg,
            settings.EMAIL_HOST_USER,
            [settings.EMAIL_HOST_USER,],
            fail_silently=False,
        )