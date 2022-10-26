from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied

def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        else:
            return view_func(request, *args, **kwargs)
    return wrapper_func


def supplier_required(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.user_type != 'supplier' or not request.user.is_superuser:
            raise PermissionDenied
        else:
            return view_func(request, *args, **kwargs)
    return wrapper_func


def retailer_required(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_superuser or request.user.user_type == 'retailer':
            return view_func(request, *args, **kwargs)
        else:
            raise PermissionDenied

    return wrapper_func