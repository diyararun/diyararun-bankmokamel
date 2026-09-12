from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import PhoneOTP, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ("phone", "first_name", "last_name", "is_staff")
    fieldsets = (
        (None, {"fields": ("phone", "password")}),
        ("اطلاعات شخصی", {"fields": ("first_name", "last_name", "email", "national_code")}),
        ("دسترسی‌ها", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("phone", "password1", "password2")}),
    )
    ordering = ("phone",)


admin.site.register(PhoneOTP)
