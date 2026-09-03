from django_jalali.db import models as jmodels
from django.db import models


class SiteSettings(models.Model):
    """Site-wide content the store owner can edit from the admin panel —
    everything that isn't a product: hero section copy, footer
    description/contact info, social links, and the About page body.

    Singleton: only one row should ever exist (enforced in save(), since
    Django has no built-in "at most one row" constraint). Always fetch it
    through SiteSettings.load(), never SiteSettings.objects.get(...).
    """

    # ---- Homepage hero section ----
    hero_title = models.CharField("عنوان هیرو", max_length=200, blank=True)
    hero_subtitle = models.CharField("زیرعنوان هیرو", max_length=200, blank=True)
    hero_description = models.TextField("توضیح هیرو", blank=True)

    # ---- Shared description (footer, and available anywhere else too) ----
    site_description = models.TextField(
        "توضیح کوتاه درباره‌ی فروشگاه", blank=True, help_text="در فوتر و بخش‌های معرفی نمایش داده می‌شود"
    )

    # ---- About page ----
    about_page_content = models.TextField(
        "محتوای کامل صفحه‌ی درباره ما",
        blank=True,
        help_text="هر پاراگراف را با یک خط خالی از پاراگراف بعدی جدا کنید",
    )

    # ---- Contact info (footer + contact page) ----
    address = models.CharField("آدرس", max_length=300, blank=True)
    phone = models.CharField("شماره تماس پشتیبانی", max_length=20, blank=True)
    email = models.EmailField("ایمیل پشتیبانی", blank=True)
    working_hours = models.CharField("ساعات پاسخگویی", max_length=100, blank=True)

    # ---- Social links ----
    instagram_url = models.URLField("لینک اینستاگرام", blank=True)
    telegram_url = models.URLField("لینک تلگرام", blank=True)
    whatsapp_url = models.URLField("لینک واتساپ", blank=True)

    updated_at = jmodels.jDateTimeField("آخرین ویرایش", auto_now=True)

    class Meta:
        verbose_name = "تنظیمات محتوای سایت"
        verbose_name_plural = "تنظیمات محتوای سایت"

    def __str__(self):
        return "تنظیمات محتوای سایت"

    def save(self, *args, **kwargs):
        # Force every save to overwrite the same single row, regardless
        # of how the instance was constructed.
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # No-op: the singleton row must never be deletable from admin
        # bulk actions (a missing row would break every page's context).
        pass

    @classmethod
    def load(cls):
        obj, _created = cls.objects.get_or_create(pk=1)
        return obj