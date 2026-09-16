from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse

# Patches Django admin so every plain number field (e.g.
# CheckoutSettings.flat_rate) accepts Persian/Arabic-indic digits — see
# the module docstring in apps/store/admin_persian_numbers.py.
import apps.store.admin_persian_numbers  # noqa: F401
from apps.store.admin_persian_numbers import PersianDigitCharAdminMixin

# Adds the "keep native browser validation errors from popping up in
# English" and "don't wipe already-chosen files on a validation error"
# fixes to every ModelAdmin — see the module docstring in
# apps/store/admin_ux_fixes.py.
import apps.store.admin_ux_fixes  # noqa: F401
from apps.store.persian_numerals import format_jalali_datetime

from .models import CheckoutSettings, Order, OrderItem


@admin.register(CheckoutSettings)
class CheckoutSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not CheckoutSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = CheckoutSettings.load()
        return redirect(reverse("admin:orders_checkoutsettings_change", args=[obj.pk]))


class OrderItemInline(admin.TabularInline):
    """Read-only snapshot of what the customer actually ordered — the
    seller must never be able to edit or add order items here. An order
    is a legal record of a completed purchase (it's what the invoice and
    tracking-code confirmation are built from); silently letting a
    seller change the product/variant/price/quantity after the fact
    would let the paper trail disagree with what the customer actually
    paid for. `variant` is included in readonly_fields (the other four
    fields already were) so the whole row — including the product-
    variant dropdown seen in the admin screenshot — is display-only, and
    `max_num = 0` + has_add_permission()=False remove the "افزودن یک
    آیتم سفارش دیگر" (add another order item) link entirely, since
    `extra = 0` / `can_delete = False` alone only stop *existing* rows
    from being deleted — they don't stop *new* ones being added.
    """

    model = OrderItem
    extra = 0
    max_num = 0
    readonly_fields = ("product_name", "variant", "variant_label", "unit_price", "quantity")
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(PersianDigitCharAdminMixin, admin.ModelAdmin):
    list_display = (
        "tracking_code",
        "user",
        "full_name",
        "phone",
        "status",
        "courier",
        "total_price",
        "created_at_display",
    )
    list_filter = ("status", "courier", "payment_method", "created_at")
    search_fields = ("tracking_code", "full_name", "phone", "user__phone", "postal_code")
    readonly_fields = (
        "tracking_code",
        "subtotal_price",
        "product_discount_amount",
        "discount_amount",
        "shipping_cost",
        "total_price",
    )
    inlines = [OrderItemInline]

    @admin.display(description="تاریخ ثبت", ordering="created_at")
    def created_at_display(self, obj):
        return format_jalali_datetime(obj.created_at)