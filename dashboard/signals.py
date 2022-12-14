from shop.models import Product
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings

from .models import Notification
from shop.models import ProductSupplier


def get_product_supplier(product):
    """
    Get the first supplier of the product.
    Email will be sent to the supplier when product is out of stock.
    """
    # TODO move to Celery
    ps = ProductSupplier.objects.filter(product=product).first()
    return (ps.supplier, ps.supplier.email)


@receiver(pre_save, sender=Product)
def create_notification(sender, instance, **kwargs):
    """
    Create notification and send email when the products
    levels is equal or is below the reorder level.
    """
    # Avoid sending duplicate notifications / spam email notifications.
    if instance.quantity <= instance.reorder_level and not instance.notification_sent:
        p_supplier = get_product_supplier(instance)
        msg_2_supplier = f"Hello {p_supplier[0]}, We, {settings.SITE_NAME} are almost running out of '{instance.name}'. Kindly prepare to resupply us with enough quantity of the product as we will specify in the order soon."
        Notification.objects.create(
            product=instance,
            supplier=p_supplier[0],
            message=msg_2_supplier,
        )

        send_mail(
            f"{settings.SITE_NAME} Stock Levels",
            msg_2_supplier,
            settings.EMAIL_HOST_USER,
            [
                p_supplier[1],
                settings.EMAIL_HOST_USER,
            ],
            fail_silently=False,
        )
        instance.notification_sent = True

    elif instance.quantity > instance.reorder_level:
        instance.notification_sent = False
