from shop.models import Product
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings

from .models import Notification


@receiver(pre_save, sender=Product)
def create_notification(sender, instance, **kwargs):
    """
    Create notification and send email when the products
    levels is equal or is below the reorder level.
    """
    # Avoid sending duplicate notifications / spam email notifications.
    if instance.quantity <= instance.reorder_level and not instance.notification_sent:
        msg = f"{instance.name} is almost running out of stock. Reorder to avoid running out of stock."
        Notification.objects.create(
            product=instance,
            message=msg,
        )
        send_mail(
            "Product Stock Levels",
            msg,
            settings.EMAIL_HOST_USER,
            [
                settings.EMAIL_HOST_USER,
            ],
            fail_silently=False,
        )
        instance.notification_sent = True

    elif instance.quantity > instance.reorder_level:
        instance.notification_sent = False
