from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django_jalali.db import models as jmodels


class SiteSettings(models.Model):
    """Site-wide content the store owner can edit from the admin panel —
    everything that isn't a product: hero copy (per page), footer/contact
    info, social links, and homepage stats.

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
    about_hero_title = models.CharField("عنوان هیرو صفحه‌ی درباره ما", max_length=200, blank=True)
    about_hero_description = models.TextField("توضیح هیرو صفحه‌ی درباره ما", blank=True)
    about_page_content = models.TextField(
        "متن تکمیلی صفحه‌ی درباره ما (اختیاری)",
        blank=True,
        help_text="در صورت پر بودن، زیر بخش آمار نمایش داده می‌شود. هر پاراگراف را با یک خط خالی جدا کنید.",
    )
    # Four number+label stat cards under the about-page hero (e.g. "+۵۰,۰۰۰ / سفارش موفق")
    stat1_number = models.CharField("آمار ۱ - عدد", max_length=30, blank=True)
    stat1_label = models.CharField("آمار ۱ - برچسب", max_length=50, blank=True)
    stat2_number = models.CharField("آمار ۲ - عدد", max_length=30, blank=True)
    stat2_label = models.CharField("آمار ۲ - برچسب", max_length=50, blank=True)
    stat3_number = models.CharField("آمار ۳ - عدد", max_length=30, blank=True)
    stat3_label = models.CharField("آمار ۳ - برچسب", max_length=50, blank=True)
    stat4_number = models.CharField("آمار ۴ - عدد", max_length=30, blank=True)
    stat4_label = models.CharField("آمار ۴ - برچسب", max_length=50, blank=True)

    # ---- Contact page hero ----
    contact_hero_title = models.CharField("عنوان هیرو صفحه‌ی تماس با ما", max_length=200, blank=True)
    contact_hero_description = models.TextField("توضیح هیرو صفحه‌ی تماس با ما", blank=True)

    # ---- Contact info (footer + contact page) ----
    address = models.CharField("آدرس", max_length=300, blank=True)
    # Free-form lists (one per line) instead of a fixed number of fields,
    # so the store owner can enter exactly as many phone numbers/emails
    # as they actually have (one, two, three...) without us guessing a
    # fixed count in the schema.
    phones = models.TextField(
        "شماره‌های تماس", blank=True, help_text="هر شماره را در یک خط جداگانه وارد کنید"
    )
    emails = models.TextField(
        "ایمیل‌ها", blank=True, help_text="هر ایمیل را در یک خط جداگانه وارد کنید"
    )
    working_hours = models.CharField("ساعات پاسخگویی", max_length=100, blank=True)

    # ---- Social links ----
    instagram_url = models.URLField("لینک اینستاگرام", blank=True)
    telegram_url = models.URLField("لینک تلگرام", blank=True)
    whatsapp_url = models.URLField("لینک واتساپ", blank=True)

    # ---- Shipping ----
    # A single flat rate, editable from the admin panel without a redeploy.
    # Per-method/per-region shipping rates are future work — this is the
    # honest match for what checkout.html actually offers today (one
    # express-delivery option, no method choice).
    express_shipping_cost = models.PositiveIntegerField(
        "هزینه ارسال اکسپرس (تومان)",
        default=49000,
        help_text="این مبلغ در صفحه‌ی تسویه‌حساب به‌عنوان هزینه‌ی ارسال به مشتری نمایش داده می‌شود.",
    )

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

    @property
    def phone_list(self):
        return [line.strip() for line in self.phones.splitlines() if line.strip()]

    @property
    def email_list(self):
        return [line.strip() for line in self.emails.splitlines() if line.strip()]


class Testimonial(models.Model):
    """A customer testimonial shown on the About page. Deliberately not
    tied to a real Review/order — this is site-wide marketing content the
    store owner curates directly, same spirit as SiteSettings.
    """

    name = models.CharField("نام", max_length=100)
    role_label = models.CharField(
        "برچسب (اختیاری)", max_length=100, blank=True, help_text='مثال: "خریدار وی پروتئین"'
    )
    rating = models.PositiveSmallIntegerField("امتیاز", validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField("متن نظر")
    display_date = models.CharField(
        "تاریخ نمایشی", max_length=50, blank=True, help_text='مثال: "تیر ۱۴۰۵" — متن آزاد، برای نمایش'
    )
    is_active = models.BooleanField("فعال (نمایش داده شود)", default=True)
    order = models.PositiveIntegerField("ترتیب نمایش", default=0)

    class Meta:
        verbose_name = "نظر مشتری (صفحه درباره ما)"
        verbose_name_plural = "نظرات مشتریان (صفحه درباره ما)"
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.name} ({self.rating}★)"

    @property
    def stars_display(self):
        return "★" * self.rating + "☆" * (5 - self.rating)


class ContactMessage(models.Model):
    """A message submitted through the "تماس با ما" form."""

    SUBJECT_CHOICES = [
        ("support", "پشتیبانی و پیگیری سفارش"),
        ("consult", "مشاوره خرید مکمل"),
        ("complaint", "انتقاد یا شکایت"),
        ("cooperation", "همکاری و مشاوره تجاری"),
    ]

    name = models.CharField("نام و نام خانوادگی", max_length=150)
    phone = models.CharField("شماره تماس", max_length=11)
    email = models.EmailField("آدرس ایمیل")
    subject = models.CharField("موضوع پیام", max_length=20, choices=SUBJECT_CHOICES)
    message = models.TextField("متن پیام")
    is_read = models.BooleanField("خوانده‌شده", default=False)
    created_at = jmodels.jDateTimeField("تاریخ ارسال", auto_now_add=True)

    class Meta:
        verbose_name = "پیام تماس با ما"
        verbose_name_plural = "پیام‌های تماس با ما"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.get_subject_display()}"