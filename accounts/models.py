from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta
from django.db.models import F

TWO_DAYS = timedelta(days=2)
TODAY = timezone.now()


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_("The Email must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        self.user_type = "retailer"

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    USER_TYPE = (
        ("SUPPLIER", "Supplier"),
        ("RETAILER", "Retailer"),
        ("CUSTOMER", "Customer"),
    )

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=255, unique=True)
    user_type = models.CharField(choices=USER_TYPE, default="CUSTOMER", max_length=10)
    is_active = models.BooleanField("Active", default=True)
    avatar = models.ImageField(
        default="avatars/default.png", upload_to="accounts/avatars"
    )
    password = models.CharField(max_length=100, editable=False)
    username = None

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name"]

    class Meta:
        db_table = "users"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.email}"

    def get_fullname(self):
        return f"{self.first_name} {self.last_name}"

    def email_exists(self):
        return User.objects.filter(email=self.email).exists()


class Supplier(models.Model):
    name = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(max_length=200)
    company_name = models.CharField(max_length=255, unique=True)
    registration_number = models.CharField(max_length=100, default="")
    store_location = models.CharField(max_length=200, default="")
    office_location = models.CharField(max_length=200, default="")
    phone = models.CharField(max_length=13, default="")
    website_url = models.CharField(max_length=255, default="")
    payment_account = models.CharField(max_length=80, default="")
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = "suppliers"

    def __str__(self):
        return self.company_name

    def currently_created(self):
        return Supplier.objects.filter(created__lte=(TODAY - TWO_DAYS))
