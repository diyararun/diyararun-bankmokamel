from django.conf import settings
from django.db import models
from django.utils.crypto import get_random_string
from django_jalali.db import models as jmodels

# Excludes 0/O and 1/I/L on purpose: those are the characters customers most
# often misread when reading a tracking code aloud on the phone with
# support, or mistype into a "track my order" field.
TRACKING_CODE_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"


class ShippingSettings(models.Model):
    """Singleton, same pattern as store.SiteSettings — lets the store
    owner change the flat shipping rate from admin instead of it being a
    hardcoded constant in views.py.
    """

    flat_rate = models.PositiveIntegerField("هزینه ارسال (تومان)", default=49000)
    updated_at = jmodels.jDateTimeField("آخرین ویرایش", auto_now=True)

    class Meta:
        verbose_name = "هزینه ارسال"
        verbose_name_plural = "هزینه ارسال"

    def __str__(self):
        return "تنظیمات هزینه‌ی ارسال"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, _created = cls.objects.get_or_create(pk=1)
        return obj


class Order(models.Model):
    """A placed order. Recipient info and address are flat fields here
    (matching checkout.html's form exactly) rather than a separate
    reusable Address model — the template has no "saved addresses" concept
    yet, so a snapshot-per-order is the honest match for what exists today.
    """

    STATUS_CHOICES = [
        ("pending_payment", "در انتظار پرداخت"),
        ("paid", "پرداخت‌شده"),
        ("processing", "در حال آماده‌سازی"),
        ("shipped", "ارسال‌شده"),
        ("delivered", "تحویل داده‌شده"),
        ("cancelled", "لغوشده"),
    ]

    # Only one option exists in checkout.html today ("پرداخت اینترنتی");
    # kept as choices (not hardcoded) so adding a second method later
    # (e.g. cash on delivery) is a one-line addition, not a schema change.
    PAYMENT_METHOD_CHOICES = [
        ("online", "پرداخت اینترنتی"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name="کاربر", related_name="orders", on_delete=models.PROTECT
    )
    status = models.CharField("وضعیت", max_length=20, choices=STATUS_CHOICES, default="pending_payment")

    # Public-facing identifier shown to the customer everywhere (order
    # history, support, future invoices) INSTEAD OF the database primary
    # key. Using `pk` directly would leak how many orders the store has
    # ever had (a sequential counter) and would be a guessable identifier
    # for a customer-facing URL/lookup — a real IDOR/enumeration concern,
    # even though every view that fetches an order also filters by
    # request.user. null=True (not a default="") so the unique constraint
    # never collides on old rows that predate this field.
    tracking_code = models.CharField(
        "کد رهگیری", max_length=20, unique=True, null=True, blank=True, editable=False, db_index=True
    )

    # ---- Section 1 of checkout.html: مشخصات تحویل‌گیرنده ----
    full_name = models.CharField("نام و نام خانوادگی", max_length=150)
    phone = models.CharField("شماره همراه", max_length=11)
    email = models.EmailField("آدرس ایمیل", blank=True)
    national_code = models.CharField("کد ملی", max_length=10, blank=True)

    # ---- Section 2 of checkout.html: آدرس دقیق محل تحویل ----
    province = models.CharField("استان", max_length=50)
    city = models.CharField("شهر", max_length=50)
    full_address = models.TextField("آدرس کامل پستی")
    postal_code = models.CharField("کد پستی", max_length=10)
    plaque = models.CharField("پلاک", max_length=20, null=True, blank=True)
    unit = models.CharField("واحد", max_length=20, blank=True)

    # ---- Section 4 of checkout.html: روش پرداخت ----
    payment_method = models.CharField(
        "روش پرداخت", max_length=20, choices=PAYMENT_METHOD_CHOICES, default="online"
    )

    # ---- Price breakdown, snapshotted at order time ----
    # Never recomputed from a live cart afterwards — prices/discounts can
    # change later, but an existing order must keep showing what the
    # customer actually agreed to pay.
    subtotal_price = models.PositiveIntegerField("جمع قیمت محصولات")
    # Informational only — the money is already reflected in subtotal_price
    # (variant.price is already the post-discount selling price). This is
    # just "how much you saved because products were on sale", snapshotted
    # because a variant's compare_at_price can change or be cleared later.
    # Separate from discount_amount below on purpose: a per-product sale
    # and a store-wide coupon/campaign (e.g. "شب یلدا") are two independent
    # discounts that must be able to stack, not one field doing both jobs.
    product_discount_amount = models.PositiveIntegerField("تخفیف محصولات", default=0)
    discount_amount = models.PositiveIntegerField("تخفیف کد تخفیف/کمپین", default=0)
    shipping_cost = models.PositiveIntegerField("هزینه ارسال", default=0)
    total_price = models.PositiveIntegerField("مبلغ نهایی قابل پرداخت")

    # Stored as typed by the customer; not validated against a real
    # Coupon model yet — that validation is the future "coupons" app's
    # job (per the earlier decision to keep it as its own module).
    coupon_code = models.CharField("کد تخفیف", max_length=50, blank=True)

    created_at = jmodels.jDateTimeField("تاریخ ثبت", auto_now_add=True)
    updated_at = jmodels.jDateTimeField("تاریخ ویرایش", auto_now=True)

    class Meta:
        verbose_name = "سفارش"
        verbose_name_plural = "سفارش‌ها"
        ordering = ["-created_at"]

    def __str__(self):
        return f"سفارش {self.tracking_code or self.pk} - {self.full_name}"

    def save(self, *args, **kwargs):
        if not self.tracking_code:
            self.tracking_code = self._generate_tracking_code()
        super().save(*args, **kwargs)

    @classmethod
    def _generate_tracking_code(cls):
        """Loops (extremely unlikely to run more than once — ~32^8
        possible codes) until it finds a code no existing order has."""
        while True:
            code = "BM-" + get_random_string(8, allowed_chars=TRACKING_CODE_ALPHABET)
            if not cls.objects.filter(tracking_code=code).exists():
                return code


class OrderItem(models.Model):
    """One product line in an order. product_name/variant_label/unit_price
    are copied from the variant AT ORDER TIME (not looked up live)
    because a product can be renamed, repriced, or even deleted later —
    an order must keep showing exactly what was actually purchased.
    """

    order = models.ForeignKey(Order, verbose_name="سفارش", related_name="items", on_delete=models.CASCADE)
    # PROTECT (not CASCADE): a variant that has ever been ordered must
    # never be deletable outright, to keep order history intact.
    variant = models.ForeignKey(
        "catalog.ProductVariant", verbose_name="تنوع محصول", related_name="order_items", on_delete=models.PROTECT
    )

    product_name = models.CharField("نام محصول", max_length=200)
    variant_label = models.CharField("برچسب وزن/سروینگ", max_length=100)
    unit_price = models.PositiveIntegerField("قیمت واحد (تومان)")
    quantity = models.PositiveIntegerField("تعداد")

    class Meta:
        verbose_name = "آیتم سفارش"
        verbose_name_plural = "آیتم‌های سفارش"

    def __str__(self):
        return f"{self.product_name} × {self.quantity}"

    @property
    def total_price(self):
        return self.unit_price * self.quantity

    @property
    def image_url(self):
        """Best-effort thumbnail from the (still-live, PROTECT-ed) variant's
        product. Mirrors apps.cart.services.serialize_cart's image lookup
        exactly, so an item looks the same in the cart drawer and in an
        order card. None if the product has no images — templates handle
        that gracefully.
        """
        images = self.variant.product.images
        image = images.filter(is_primary=True).first() or images.first()
        return image.image.url if image else None