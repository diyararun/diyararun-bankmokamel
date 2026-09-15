from django.contrib import admin

# Adds the "keep native browser validation errors from popping up in
# English" and "don't wipe already-chosen files on a validation error"
# fixes to every ModelAdmin — see the module docstring in
# apps/store/admin_ux_fixes.py.
import apps.store.admin_ux_fixes  # noqa: F401
from apps.store.persian_numerals import format_jalali_datetime

from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ("added_at_display",)

    @admin.display(description="تاریخ افزودن")
    def added_at_display(self, obj):
        return format_jalali_datetime(obj.added_at)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "session_key", "total_quantity", "total_price", "updated_at_display")
    list_filter = ("updated_at",)
    search_fields = ("user__phone", "session_key")
    inlines = [CartItemInline]

    @admin.display(description="آخرین ویرایش", ordering="updated_at")
    def updated_at_display(self, obj):
        return format_jalali_datetime(obj.updated_at)