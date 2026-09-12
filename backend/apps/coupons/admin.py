from django.contrib import admin

import django_jalali.admin  # noqa: F401  (Jalali widget for date fields)

# Patches Django admin so every plain number field (value, min/max
# order amount, usage limit, ...) accepts Persian/Arabic-indic digits —
# see the module docstring in apps/store/admin_persian_numbers.py.
import apps.store.admin_persian_numbers  # noqa: F401

from .models import Coupon, CouponRedemption


class CouponRedemptionInline(admin.TabularInline):
    model = CouponRedemption
    extra = 0
    can_delete = False
    readonly_fields = ("user", "order", "redeemed_at")

    def has_add_permission(self, request, obj=None):
        # Redemptions only ever get created by CheckoutView.post() — never
        # by hand in admin, since that would bypass the one-per-user check.
        return False


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "discount_type",
        "value",
        "is_active",
        "used_count",
        "usage_limit",
        "valid_from",
        "valid_until",
    )
    list_filter = ("discount_type", "is_active")
    search_fields = ("code",)
    readonly_fields = ("used_count", "created_at")
    fieldsets = (
        (None, {"fields": ("code", "is_active")}),
        ("تخفیف", {"fields": ("discount_type", "value", "max_discount_amount", "min_order_amount")}),
        ("محدودیت‌ها", {"fields": ("usage_limit", "used_count", "valid_from", "valid_until")}),
    )
    inlines = [CouponRedemptionInline]