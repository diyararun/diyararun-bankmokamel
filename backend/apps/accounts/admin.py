from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.store.admin_persian_numbers import PersianDigitCharAdminMixin

# Adds the "keep native browser validation errors from popping up in
# English" and "don't wipe already-chosen files on a validation error"
# fixes to every ModelAdmin — see the module docstring in
# apps/store/admin_ux_fixes.py.
import apps.store.admin_ux_fixes  # noqa: F401
from apps.store.persian_numerals import format_jalali_datetime

from .models import Address, PhoneOTP, User


@admin.register(User)
class CustomUserAdmin(PersianDigitCharAdminMixin, UserAdmin):
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


@admin.register(Address)
class AddressAdmin(PersianDigitCharAdminMixin, admin.ModelAdmin):
    list_display = ("title", "user", "full_name", "phone", "city", "is_default", "created_at_display")
    list_filter = ("is_default", "province")
    search_fields = ("full_name", "phone", "user__phone", "city", "full_address")

    @admin.display(description="تاریخ ثبت", ordering="created_at")
    def created_at_display(self, obj):
        return format_jalali_datetime(obj.created_at)
