from django.conf import settings
from django.db import models
from django_jalali.db import models as jmodels


class Cart(models.Model):
    """A shopping cart, belonging to either a logged-in user OR an
    anonymous session — never both, and never neither (enforced at the
    application layer in services.get_cart, not here at the DB level,
    since a CHECK constraint on "exactly one of two nullable FKs" needs
    raw SQL and isn't worth it for a table this small).

    Guest carts (session_key set, user NULL) are not yet merged into the
    user's cart on login — that merge logic is a follow-up, not part of
    this pass.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name="کاربر", null=True, blank=True, related_name="carts", on_delete=models.CASCADE
    )
    session_key = models.CharField("کلید نشست", max_length=40, null=True, blank=True, db_index=True)
    created_at = jmodels.jDateTimeField("تاریخ ایجاد", auto_now_add=True)
    updated_at = jmodels.jDateTimeField("تاریخ ویرایش", auto_now=True)

    class Meta:
        verbose_name = "سبد خرید"
        verbose_name_plural = "سبدهای خرید"
        ordering = ["-updated_at"]

    def __str__(self):
        return f"سبد #{self.pk} - {self.user or self.session_key}"

    @property
    def total_quantity(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())


class CartItem(models.Model):
    """One product variant + quantity line in a cart. Points at
    ProductVariant (not Product) since price/stock live on the variant —
    a cart line always means a specific flavor/weight combination.
    """

    cart = models.ForeignKey(Cart, verbose_name="سبد خرید", related_name="items", on_delete=models.CASCADE)
    variant = models.ForeignKey(
        "catalog.ProductVariant", verbose_name="تنوع محصول", related_name="cart_items", on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField("تعداد", default=1)
    added_at = jmodels.jDateTimeField("تاریخ افزودن", auto_now_add=True)

    class Meta:
        verbose_name = "آیتم سبد خرید"
        verbose_name_plural = "آیتم‌های سبد خرید"
        unique_together = ("cart", "variant")

    def __str__(self):
        return f"{self.variant} × {self.quantity}"

    @property
    def unit_price(self):
        return self.variant.price

    @property
    def total_price(self):
        return self.variant.price * self.quantity