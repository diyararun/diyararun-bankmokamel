from django.conf import settings
from django.db import models
from django_jalali.db import models as jmodels


class Coupon(models.Model):
    """A discount code the seller creates and manages entirely from the
    admin panel. Validity rules (active flag, date window, usage caps,
    minimum order amount) are enforced by apps.coupons.services.validate_coupon
    — never trust a discount amount computed in the browser; checkout
    re-runs this same validation server-side before creating the Order.
    """

    class DiscountType(models.TextChoices):
        PERCENT = "percent", "درصدی"
        FIXED = "fixed", "مبلغ ثابت"

    # Stored upper-cased (see save()) so "yalda10" and "YALDA10" are the
    # same code — customers shouldn't lose a discount over letter casing.
    code = models.CharField("کد تخفیف", max_length=50, unique=True)
    discount_type = models.CharField(
        "نوع تخفیف", max_length=10, choices=DiscountType.choices, default=DiscountType.PERCENT
    )
    value = models.PositiveIntegerField(
        "مقدار تخفیف",
        help_text="برای نوع «درصدی» عددی بین ۱ تا ۱۰۰؛ برای نوع «مبلغ ثابت» مبلغ به تومان.",
    )
    max_discount_amount = models.PositiveIntegerField(
        "سقف مبلغ تخفیف (تومان)",
        null=True,
        blank=True,
        help_text="فقط برای نوع «درصدی» — تخفیف محاسبه‌شده هیچ‌وقت از این مبلغ بیشتر نمی‌شود. برای «مبلغ ثابت» بی‌اثر است.",
    )
    min_order_amount = models.PositiveIntegerField(
        "حداقل مبلغ سبد خرید (تومان)",
        default=0,
        help_text="کد فقط روی سبدهایی با قیمت محصولات حداقل به این مقدار قابل اعمال است.",
    )
    usage_limit = models.PositiveIntegerField(
        "سقف تعداد کل استفاده",
        null=True,
        blank=True,
        help_text="خالی بگذارید یعنی بدون محدودیت.",
    )
    used_count = models.PositiveIntegerField("تعداد استفاده‌شده", default=0, editable=False)
    # Per-user limit is fixed at "once" (not a configurable number) — the
    # project's own decision was "هر کاربر فقط یک‌بار"، not a per-coupon
    # setting; apps.coupons.models.CouponRedemption is what enforces it.
    valid_from = jmodels.jDateTimeField("تاریخ شروع اعتبار", null=True, blank=True)
    valid_until = jmodels.jDateTimeField("تاریخ پایان اعتبار", null=True, blank=True)
    is_active = models.BooleanField("فعال", default=True)
    created_at = jmodels.jDateTimeField("تاریخ ساخت", auto_now_add=True)

    class Meta:
        verbose_name = "کد تخفیف"
        verbose_name_plural = "کدهای تخفیف"
        ordering = ["-created_at"]

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        self.code = self.code.strip().upper()
        super().save(*args, **kwargs)

    def calculate_discount(self, subtotal):
        """Toman amount this coupon takes off a cart whose product
        subtotal (after per-item sale prices, before shipping) is
        `subtotal`. Never returns more than `subtotal` itself — a coupon
        discounting more than the order is worth would make total_price
        negative downstream.
        """
        if self.discount_type == self.DiscountType.PERCENT:
            amount = subtotal * self.value // 100
            if self.max_discount_amount is not None:
                amount = min(amount, self.max_discount_amount)
        else:
            amount = self.value
        return min(amount, subtotal)


class CouponRedemption(models.Model):
    """One row per successful use of a coupon on an order. This is what
    "هر کاربر فقط یک‌بار" is actually enforced against (a query for an
    existing redemption by this user+coupon), and doubles as an audit
    trail — which customer used which code, on which order, and when.
    """

    coupon = models.ForeignKey(Coupon, on_delete=models.PROTECT, related_name="redemptions", verbose_name="کد تخفیف")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="coupon_redemptions", verbose_name="کاربر"
    )
    order = models.OneToOneField(
        "orders.Order", on_delete=models.CASCADE, related_name="coupon_redemption", verbose_name="سفارش"
    )
    redeemed_at = jmodels.jDateTimeField("تاریخ استفاده", auto_now_add=True)

    class Meta:
        verbose_name = "استفاده از کد تخفیف"
        verbose_name_plural = "استفاده‌های کد تخفیف"
        ordering = ["-redeemed_at"]

    def __str__(self):
        return f"{self.coupon.code} — {self.user}"