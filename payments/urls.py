from django.urls import path

from . views import (
    lipa_na_mpesa_online,
    register_urls, confirmation, validation,
    call_back
)

urlpatterns = [
    path('online/lipa/', lipa_na_mpesa_online, name='lipa_na_mpesa'),
    path("c2b/register/", register_urls, name='register_mpesa_validation'),
    path('c2b/confirmation/', confirmation, name='confirmation'),
    path('c2b/validation/', validation, name='validation'),
    path('c2b/callback/', call_back, name='call_back'),
]