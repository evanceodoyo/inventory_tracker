from django.urls import path
from . views import (sign_up, login_view,
logout_view, profile, password_reset, password_change, supplier_update)
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('sign-up/', sign_up, name='sign_up'),
    path('login/', login_view, name='login'),
    path('profile/', profile, name='profile'),
    path('profile/supplier-update/', supplier_update, name="supplier_update"),
    path('password-change/', password_change, name="password_change"),
    path('password-reset/', password_reset, name='password_reset'),
    path('password-reset-done/', auth_views.PasswordResetDoneView.as_view(template_name='password-reset-done.html'), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password-reset-confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='password-reset-complete.html'), name='password_reset_complete'),
    path('logout/', logout_view, name='logout'),
]
