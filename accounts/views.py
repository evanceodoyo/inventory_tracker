from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
from .decorators import unauthenticated_user, supplier_required
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from shop.models import Order, ShippingAddress, Product, ProductSupplier
from django.core.mail import send_mail, BadHeaderError
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.db import transaction
from . models import Supplier

User = get_user_model()

def validate_user(user):
    error_msg = None
    if not user.first_name:
        error_msg = "First Name required!"
    elif not user.last_name:
        error_msg = "Last Name required"
    elif not user.email:
        error_msg = "Email required"
    elif user.email_exists():
        error_msg = "A user with the email already exists"
    # elif not user.password:
    #     error_msg = "Password required!"
    return error_msg

@unauthenticated_user
def sign_up(request):
    context = {}
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        user_type = request.POST.get('user_type')
        password = request.POST.get('password')

        user = User(
            first_name = first_name,
            last_name = last_name,
            email = email,
        )

        if error_msg := validate_user(user):
            messages.error(request, error_msg)
        else:
            if user_type == 'supplier':
                user.user_type = 'supplier'
            user.set_password(password)
            user.save()
            if user := authenticate(request, username=email, password=password):
                login(request, user)
                return redirect("home")
        context = {"page_title": "Sign Up", "email": email, 'first_name': first_name, "last_name": last_name}
    return render(request, 'signup.html', context)

@unauthenticated_user
def login_view(request):
    context = {"page_title": "Login"}
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        context['email'] = email

        if user := authenticate(request, username=email, password=password):
            login(request, user)
            messages.success(request, "Login successful")
            if "next" in request.POST:
                return redirect(request.POST.get("next"))
            return redirect("home")

        else:
            messages.error(request, "Invalid email or password")

    return render(request, 'login.html', context)

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully')
    return redirect("login")

@login_required
def profile(request):
    try:
        user = request.user
        user = User.objects.get(id=user.id)
        orders = Order.objects.filter(customer=user)[:10]
        shipping_address = ShippingAddress.objects.filter(customer=user).first()
        context = {"page_title": "Profile", "user": user, "addr": shipping_address, 'orders': orders}
        if request.method == 'POST':
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            street = request.POST.get('street')
            apartment = request.POST.get('apartment')
            phone = request.POST.get('phone')

            user.first_name = first_name
            user.last_name = last_name
            user.save()
            if shipping_address:
                shipping_address.street = street
                shipping_address.apartment = apartment
                shipping_address.phone = phone
                shipping_address.save()
            else:
                shipping_address = ShippingAddress.objects.create(customer=user, street=street, apartment=apartment, phone=phone)
            messages.success(request, 'Profile update successfull')
            return redirect('profile')
        if user.user_type == 'supplier':
            supplier = Supplier.objects.get(name=user)
            products = Product.objects.all()
            context['supplier'] = supplier
            context['products'] = products
        return render(request, 'account.html', context)
        
    except User.DoesNotExist:
        raise Http404


@login_required
def password_change(request):
    user = User.objects.get(id=request.user.id)
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        new_password2 = request.POST.get('new_password2')

        if new_password != new_password2:
            messages.error(request, "Confirm the password.")
            return redirect('profile')
       
        if user := authenticate(request, username=user.email, password=old_password):
            subject = "Password Reset"
            email_template_name = 'password_reset_email.txt'
            sent_from = settings.EMAIL_HOST_USER
            d = {
                "email": user.email,
                'domain': '127.0.0.1:8000',
                'uid': urlsafe_base64_encode(force_bytes(user.id)),
                "user": user,
                'site_name': settings.SITE_NAME,
                "token": default_token_generator.make_token(user),
                "protocol": 'http',
            }

            mail = render_to_string(email_template_name, d)
            try:
                send_mail(subject, mail, sent_from, [user.email], fail_silently=False)
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            logout(request)
            return redirect('password_reset_done')
        else:
            messages.error(request, 'The old password entered is wrong.')
    return redirect('profile')


def password_reset(request):
    context = {"page_title": 'Password Reset'}
    if request.method ==  'POST':
        email = request.POST.get('email')
        
        # Check if the user exists
        if user := get_object_or_404(User, email=email):
            subject = "Password Reset"
            email_template_name = 'password_reset_email.txt'
            sent_from = settings.EMAIL_HOST_USER
            
            d = {
                "email": user.email,
                'domain': '127.0.0.1:8000',
                'uid': urlsafe_base64_encode(force_bytes(user.id)),
                "user": user,
                'site_name': settings.SITE_NAME,
                "token": default_token_generator.make_token(user),
                "protocol": 'http',
            }

            mail = render_to_string(email_template_name, d)
            try:
                send_mail(subject, mail, sent_from, [user.email], fail_silently=False)
            except BadHeaderError:
                return HttpResponse('Invalid header found.')

            return redirect('password_reset_done')
        else:
            messages.error(request, 'No user with such email in our database.')
            return redirect('password_reset')
    return render(request, 'password-reset-form.html', context)


@login_required
@supplier_required
@transaction.atomic
def supplier_update(request):
    user = User.objects.get(id=request.user.id)
    if request.method == 'POST':
        company_name = request.POST.get('company_name')
        store_location = request.POST.get('store_location')
        office_location = request.POST.get('office_location')
        phone = request.POST.get('phone')
        website_url = request.POST.get('website_url')
        registration_number = request.POST.get('registration_number')
        payment_account = request.POST.get('payment_account')
        products_supplied = request.POST.getlist('products_supplied')
        products = Product.get_products_by_ids(products_supplied)

        try:
            supplier = Supplier.objects.get(name=user)
            supplier.name = user
            supplier.company_name = company_name
            supplier.store_location = store_location
            supplier.office_location = office_location
            supplier.phone = phone
            supplier.website_url = website_url
            supplier.registration_number = registration_number
            supplier.payment_account = payment_account
            supplier.save()
            # supplier_products = supplier.products.all()
            # supplier.products.set(products)
            messages.success(request, "Company details updated successfully")
            return redirect('profile')
        except Supplier.DoesNotExist:
            supplier = Supplier.objects.create(
                name = user,
                company_name = company_name,
                store_location = store_location,
                office_location = office_location,
                phone = phone,
                website_url = website_url,
                registration_number = registration_number,
                payment_account = payment_account,
            )
            for product in products:
                ProductSupplier.objects.create(
                    supplier = supplier,
                    product = product
                )
            messages.success(request, "Company details created successfully")
            return redirect('profile')

    return redirect('profile')
        