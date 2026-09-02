from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product_name", "variant_label", "unit_price", "quantity")
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "phone", "status", "total_price", "created_at")
    list_filter = ("status", "payment_method", "created_at")
    search_fields = ("full_name", "phone", "user__phone", "postal_code")
    readonly_fields = ("subtotal_price", "discount_amount", "shipping_cost", "total_price")
    inlines = [OrderItemInline]