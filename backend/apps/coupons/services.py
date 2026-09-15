from django.utils import timezone

from .models import Coupon, CouponRedemption


def validate_coupon(code, user, subtotal, *, lock=False):
    """Checks a coupon code against every rule that can make it
    inapplicable right now, for this user, for this cart subtotal.

    Returns (coupon, discount_amount, error_message) — exactly one of
    `coupon` or `error_message` is meaningful: on success `error_message`
    is None, on failure `coupon` is None and `discount_amount` is 0.

    Called from two places on purpose: apps.coupons.views.ApplyCouponView
    (for the instant "اعمال" button, so the customer gets feedback before
    submitting) and orders.views.CheckoutView.post (which re-runs this
    exact check server-side — the AJAX result is never trusted as-is,
    since the coupon could expire, hit its usage cap, or get deactivated
    in the gap between the two calls).

    lock=True takes a row lock (SELECT ... FOR UPDATE) on the coupon —
    only valid inside an open transaction. CheckoutView.post passes this
    so two customers racing for the last unit of a usage-limited coupon
    can't both pass the used_count check before either commits; the AJAX
    preview call doesn't need it since it isn't reserving anything.
    """
    code = (code or "").strip()
    if not code:
        return None, 0, "کد تخفیف را وارد کنید."

    qs = Coupon.objects.select_for_update() if lock else Coupon.objects
    try:
        coupon = qs.get(code__iexact=code)
    except Coupon.DoesNotExist:
        return None, 0, "کد تخفیف نامعتبر است."

    if not coupon.is_active:
        return None, 0, "این کد تخفیف غیرفعال است."

    now = timezone.now()
    if coupon.valid_from and now < coupon.valid_from:
        return None, 0, "این کد تخفیف هنوز فعال نشده است."
    if coupon.valid_until and now > coupon.valid_until:
        return None, 0, "تاریخ اعتبار این کد تخفیف به پایان رسیده است."

    if coupon.usage_limit is not None and coupon.used_count >= coupon.usage_limit:
        return None, 0, "ظرفیت استفاده از این کد تخفیف تکمیل شده است."

    if CouponRedemption.objects.filter(coupon=coupon, user=user).exists():
        return None, 0, "شما قبلاً از این کد تخفیف استفاده کرده‌اید."

    if subtotal < coupon.min_order_amount:
        return None, 0, f"این کد فقط برای سبدهای بالای {coupon.min_order_amount} تومان معتبر است."

    if subtotal <= 0:
        return None, 0, "سبد خرید شما خالی است."

    discount_amount = coupon.calculate_discount(subtotal)
    return coupon, discount_amount, None