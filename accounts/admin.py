from django.contrib import admin
from .models import Supplier, User


class UserAdmin(admin.ModelAdmin):
    list_display = ["get_full_name", "email", "user_type", "last_login"]


admin.site.register(User, UserAdmin)
admin.site.register(Supplier)
