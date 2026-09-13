from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse

# Patches Django admin so every plain number field (e.g.
# ShippingSettings.flat_rate) accepts Persian/Arabic-indic digits — see
# the module docstring in apps/store/admin_persian_numbers.py.
import apps.store.admin_persian_numbers  # noqa: F401

from .models import Order, OrderItem, ShippingSettings


@admin.register(ShippingSettings)
class ShippingSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not ShippingSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = ShippingSettings.load()
        return redirect(reverse("admin:orders_shippingsettings_change", args=[obj.pk]))


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product_name", "variant_label", "unit_price", "quantity")
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("tracking_code", "user", "full_name", "phone", "status", "total_price", "created_at")
    list_filter = ("status", "payment_method", "created_at")
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