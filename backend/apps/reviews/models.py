from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django_jalali.db import models as jmodels


class Review(models.Model):
    """A customer review, held for moderation ("نظرات شما پس از تایید
    مدیریت نمایش داده می‌شوند" per the template) before it becomes public.

    Lives in its own app (separate from catalog) since reviews are a
    self-contained, reusable concern — the same pattern will be used for
    the future coupons app.

    is_verified_purchase defaults to False here; it should be set to True
    automatically once the orders app (Phase 2) can confirm the reviewer
    actually bought this product — that wiring happens then, not now.
    """

    # String reference (app_label.ModelName) instead of importing the
    # Product class directly, so this app has no hard Python import
    # dependency on catalog — only a migration-level dependency.
    product = models.ForeignKey(
        "catalog.Product", verbose_name="محصول", related_name="reviews", on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name="کاربر", related_name="reviews", on_delete=models.CASCADE
    )
    rating = models.PositiveSmallIntegerField("امتیاز", validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField("متن نظر")
    is_verified_purchase = models.BooleanField("خریدار محصول", default=False)
    is_approved = models.BooleanField("تاییدشده", default=False)
    created_at = jmodels.jDateTimeField("تاریخ ثبت", auto_now_add=True)

    class Meta:
        verbose_name = "نظر"
        verbose_name_plural = "نظرات"
        ordering = ["-created_at"]
        unique_together = ("product", "user")

    def __str__(self):
        return f"{self.user} - {self.product.name} ({self.rating}★)"
