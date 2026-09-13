from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import F
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import View

from apps.accounts.models import Address
from apps.cart.services import get_cart, product_discount_total, serialize_cart
from apps.coupons.models import Coupon, CouponRedemption
from apps.coupons.services import validate_coupon

from .forms import CheckoutForm
from .models import Order, OrderItem, ShippingSettings


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
        form = CheckoutForm(initial=self._initial_data(request.user))
        return render(request, self.template_name, self._context(form, cart))

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
        shipping_cost = ShippingSettings.load().flat_rate
        coupon_code = form.cleaned_data.get("coupon_code")

        # Order creation, the coupon redemption, the profile update, and
        # clearing the cart must all succeed together or not at all — an
        # order that exists without its items (or a half-cleared cart, or
        # a coupon marked used without an order to show for it) would
        # corrupt the customer's next visit.
        with transaction.atomic():
            coupon = None
            discount_amount = 0
            if coupon_code:
                # lock=True takes a row lock on this Coupon for the rest of
                # the transaction — without it, two customers racing for
                # the last unit of a usage-limited code could both pass
                # the used_count check before either commits, handing out
                # one more redemption than the limit allows.
                coupon, discount_amount, error = validate_coupon(
                    coupon_code, request.user, subtotal, lock=True
                )
                if error:
                    form.add_error("coupon_code", error)
                    return render(request, self.template_name, self._context(form, cart))

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

            if coupon:
                CouponRedemption.objects.create(coupon=coupon, user=request.user, order=order)
                # F() so this is an atomic "used_count = used_count + 1" at
                # the database level — reading, incrementing, and saving
                # the Python int back would race with the lock above doing
                # nothing to protect it.
                Coupon.objects.filter(pk=coupon.pk).update(used_count=F("used_count") + 1)

            # The checkout form is also the first place the user ever
            # types their email/national code, so save it straight to
            # their account — no reason to make them re-enter it later
            # on the profile page.
            user = request.user
            user.email = form.cleaned_data["email"] or user.email
            user.national_code = form.cleaned_data["national_code"] or user.national_code
            user.save(update_fields=["email", "national_code"])

            # اولین باری که این کاربر سفارش ثبت می‌کند، همان آدرسی که همین‌جا
            # وارد کرده را به‌عنوان اولین ردیف «آدرس‌های من» ذخیره می‌کنیم —
            # طبق خواسته‌ی صریح: تا از خرید دوم به بعد، همین آدرس خودکار در
            # فرم پر شود (_initial_data زیر دقیقاً همین ردیف را می‌خواند)،
            # بدون این‌که کاربر مجبور شود جداگانه به صفحه‌ی «آدرس‌های من»
            # برود و همان اطلاعات را دوباره تایپ کند. اگر کاربر از قبل
            # (دستی، از همان صفحه) یک آدرس ثبت کرده باشد، این‌جا کاری
            # نمی‌کنیم — فقط "اولین آدرس وارد‌شده" ذخیره می‌شود، نه هر
            # سفارش. عنوان «آدرس من» یک نام پیش‌فرض خنثی است؛ کاربر بعداً
            # می‌تواند آن را از همان صفحه ویرایش/تغییرنام دهد.
            if not user.addresses.exists():
                Address.objects.create(
                    user=user,
                    title="آدرس من",
                    full_name=form.cleaned_data["full_name"],
                    phone=form.cleaned_data["phone"],
                    province=form.cleaned_data["province"],
                    city=form.cleaned_data["city"],
                    full_address=form.cleaned_data["full_address"],
                    postal_code=form.cleaned_data["postal_code"],
                    plaque=form.cleaned_data["plaque"],
                    unit=form.cleaned_data["unit"],
                    is_default=True,
                )

        messages.success(request, f"سفارش شما با کد پیگیری {order.tracking_code} با موفقیت ثبت شد.")
        # به جای لیست کلی سفارش‌ها، مستقیم به جزئیات همین سفارش می‌رویم —
        # همان صفحه‌ای که هدر آن گام سوم استپر ("تکمیل و دریافت فاکتور") را
        # نشان می‌دهد و دکمه‌ی پرداخت آزمایشی/دریافت فاکتور را دارد
        # (accounts/order_detail.html، به‌شرط status="pending_payment").
        return redirect(reverse("accounts:order_detail", kwargs={"tracking_code": order.tracking_code}))

    def _initial_data(self, user):
        """Pre-fills the checkout form so a returning customer never has
        to retype what the store already knows about them — exactly what
        was asked: recipient/address fields default from whatever's on
        file, instead of a blank form every single time.

        Two independent sources, layered (later one wins where both
        have an opinion):

        1. The user's most recent previous order, if any — covers every
           customer who bought before the "آدرس‌های من" address book
           existed, and doubles as a sane fallback for email/national_code
           (which Address doesn't store at all).
        2. The user's default Address, if any — more likely to be
           current, since it's the one thing a customer can go edit on
           its own page without that changing any past order's snapshot.
           CheckoutView.post() above auto-creates this from a user's
           very first order, so from their second purchase onward this
           branch is normally what actually fires.
        """
        initial = {}

        last_order = user.orders.order_by("-created_at").first()
        if last_order:
            initial.update(
                {
                    "full_name": last_order.full_name,
                    "phone": last_order.phone,
                    "email": last_order.email,
                    "national_code": last_order.national_code,
                    "province": last_order.province,
                    "city": last_order.city,
                    "full_address": last_order.full_address,
                    "postal_code": last_order.postal_code,
                    "plaque": last_order.plaque,
                    "unit": last_order.unit,
                }
            )
        else:
            # اولین خرید — دست‌کم چیزی که از قبل در پروفایل ثبت شده (اگر
            # کاربر پیش‌تر از صفحه‌ی پروفایل ایمیل/کدملی را وارد کرده
            # باشد) را پر می‌کنیم؛ بقیه‌ی فیلدها همچنان خالی می‌مانند.
            if user.email:
                initial["email"] = user.email
            if user.national_code:
                initial["national_code"] = user.national_code

        default_address = user.addresses.filter(is_default=True).first()
        if default_address:
            initial.update(
                {
                    "full_name": default_address.full_name,
                    "phone": default_address.phone,
                    "province": default_address.province,
                    "city": default_address.city,
                    "full_address": default_address.full_address,
                    "postal_code": default_address.postal_code,
                    "plaque": default_address.plaque,
                    "unit": default_address.unit,
                }
            )

        return initial

    def _context(self, form, cart):
        # The sidebar order summary shows the shipping cost, product
        # discount, and final total *before* the order actually exists, so
        # they're computed here from the live cart + current ShippingSettings,
        # the same way post() computes them for the real Order — kept in
        # sync deliberately, not copied.
        cart_data = serialize_cart(cart)
        shipping_cost = ShippingSettings.load().flat_rate
        subtotal = cart_data["total_price"]

        # If a coupon is already sitting in the (possibly re-rendered
        # after some other field's error) form, keep showing its discount
        # instead of silently dropping it just because this is a
        # re-render rather than the customer's first look at the page.
        # No lock here — this is read-only display, not a reservation.
        coupon_discount_amount = 0
        if form.is_bound:
            coupon_code = form.data.get("coupon_code", "")
            if coupon_code:
                _coupon, coupon_discount_amount, _error = validate_coupon(
                    coupon_code, self.request.user, subtotal
                )

        return {
            "form": form,
            "cart": cart_data,
            "product_discount_amount": product_discount_total(cart_data),
            "coupon_discount_amount": coupon_discount_amount,
            "shipping_cost": shipping_cost,
            "final_total_price": subtotal - coupon_discount_amount + shipping_cost,
            "active_nav": "checkout",
        }