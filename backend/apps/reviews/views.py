from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import View

from apps.cart.services import get_cart, serialize_cart

from .forms import CheckoutForm
from .models import Order, OrderItem

# Flat shipping cost for now — no shipping-rate calculation exists yet.
# TODO: replace with a real rule once that logic is built.
FLAT_SHIPPING_COST = 49000


class CheckoutView(LoginRequiredMixin, View):
    """GET renders the checkout page (recipient/address/payment form +
    order summary from the real cart). POST validates the form and, if
    the cart isn't empty, creates the Order + OrderItem rows and clears
    the cart.

    No payment gateway integration yet — that's Phase 3 of the roadmap.
    The order is created with status="pending_payment" and the customer
    is redirected with a success message; actually charging them is
    future work, not part of this pass.
    """

    template_name = "orders/checkout.html"

    def get(self, request):
        cart = get_cart(request, create=False)
        return render(request, self.template_name, self._context(CheckoutForm(), cart))

    def post(self, request):
        cart = get_cart(request, create=False)
        cart_data = serialize_cart(cart)

        if not cart_data["items"]:
            messages.error(request, "سبد خرید شما خالی است.")
            return redirect(reverse("store:index"))

        form = CheckoutForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, self._context(form, cart))

        subtotal = cart_data["total_price"]
        shipping_cost = FLAT_SHIPPING_COST
        discount_amount = 0  # real coupon validation is the future "coupons" app's job

        order = Order.objects.create(
            user=request.user,
            subtotal_price=subtotal,
            discount_amount=discount_amount,
            shipping_cost=shipping_cost,
            total_price=subtotal - discount_amount + shipping_cost,
            **form.cleaned_data,
        )
        for item in cart.items.select_related("variant__product").all():
            OrderItem.objects.create(
                order=order,
                variant=item.variant,
                product_name=item.variant.product.name,
                variant_label=item.variant.label,
                unit_price=item.variant.price,
                quantity=item.quantity,
            )
        cart.items.all().delete()

        messages.success(request, f"سفارش شما با شماره #{order.pk} با موفقیت ثبت شد.")
        return redirect(reverse("store:index"))

    def _context(self, form, cart):
        return {"form": form, "cart": serialize_cart(cart), "active_nav": "checkout"}