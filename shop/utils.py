import random
import string


def random_string_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return "".join(random.choice(chars) for _ in range(size))


def unique_order_id_generator(instance):
    """
    Generates a unique order ID for every order.
    """
    new_order_id = random_string_generator()
    Klass = instance.__class__
    if Klass.objects.filter(order_id=new_order_id).exists():
        return unique_order_id_generator(instance)
    return new_order_id
