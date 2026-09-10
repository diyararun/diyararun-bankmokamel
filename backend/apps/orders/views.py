from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import View

from apps.cart.services import get_cart, product_discount_total, serialize_cart
from apps.store.models import SiteSettings

from .forms import CheckoutForm
from .models import Order, OrderItem


class CheckoutView(LoginRequiredMixin, View):
    """GET renders the checkout page (recipient/address/payment form +
    order summary from the real cart). POST validates the form and, if
    the cart isn't empty, creates the Order + OrderItem rows, saves the
    profile fields the checkout form also collects (email, national
    code) onto the user, and clears the cart.

    No payment gateway integration yet — that's a later phase of the
    roadmap. The order is deliberately created with
    status="pending_payment" *before* any redirect to a gateway would
    happen: if payment later fails or the customer never comes back,
    the order (and its items) must still exist so they can retry —
    losing the cart on a failed payment would be a real loss for them.
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
        shipping_cost = SiteSettings.load().express_shipping_cost
        discount_amount = 0  # real coupon/campaign validation is the future "coupons" app's job

        # Order creation, the profile update, and clearing the cart must
        # all succeed together or not at all — an order that exists
        # without its items (or a half-cleared cart) would corrupt the
        # customer's next visit.
        with transaction.atomic():
            order = Order.objects.create(
                user=request.user,
                subtotal_price=subtotal,
                product_discount_amount=product_discount_total(cart_data),
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

            # The checkout form is also the first place the user ever
            # types their email/national code, so save it straight to
            # their account — no reason to make them re-enter it later
            # on the profile page. The address itself is NOT copied here:
            # it stays a per-order snapshot until the future "my
            # addresses" feature gives users a reusable address book.
            user = request.user
            user.email = form.cleaned_data["email"] or user.email
            user.national_code = form.cleaned_data["national_code"] or user.national_code
            user.save(update_fields=["email", "national_code"])

        messages.success(request, f"سفارش شما با کد پیگیری {order.tracking_code} با موفقیت ثبت شد.")
        return redirect(reverse("accounts:orders"))

    def _context(self, form, cart):
        # The sidebar order summary shows the shipping cost, product
        # discount, and final total *before* the order actually exists, so
        # they're computed here from the live cart + current SiteSettings,
        # the same way post() computes them for the real Order — kept in
        # sync deliberately, not copied.
        cart_data = serialize_cart(cart)
        shipping_cost = SiteSettings.load().express_shipping_cost
        return {
            "form": form,
            "cart": cart_data,
            "product_discount_amount": product_discount_total(cart_data),
            "shipping_cost": shipping_cost,
            "final_total_price": cart_data["total_price"] + shipping_cost,
            "active_nav": "checkout",
        }