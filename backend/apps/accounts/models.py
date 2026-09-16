import random

from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django_jalali.db import models as jmodels


class UserManager(BaseUserManager):
    """Custom manager, required because USERNAME_FIELD is "phone" instead
    of Django's default "username". The built-in UserManager that
    AbstractUser normally provides hardcodes a "username" positional
    argument in create_user/create_superuser regardless of USERNAME_FIELD,
    which breaks `manage.py createsuperuser` for this model."""

    use_in_migrations = True

    def _create_user(self, phone, password, **extra_fields):
        if not phone:
            raise ValueError("شماره موبایل الزامی است")
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(phone, password, **extra_fields)

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(phone, password, **extra_fields)


class User(AbstractUser):
    """
    کاربر بر اساس شماره موبایل (متناسب با فرم ورود/ثبت‌نام پیامکی سایت).
    """

    # Fully remove the inherited "username" field instead of just ignoring
    # it — AbstractUser's username is unique=True with no default, so
    # leaving it in place would make every user default to username="",
    # and the SECOND such user would fail on the unique constraint.
    username = None

    phone = models.CharField("شماره موبایل", max_length=11, unique=True)
    national_code = models.CharField("کد ملی", max_length=10, blank=True)
    avatar_emoji = models.CharField("آیکون پروفایل", max_length=4, default="👤")
    # Temporary single-address convenience field, filled automatically from
    # checkout — superseded once the real "آدرس‌های من" address book (with
    # multiple saved addresses) is built.
    address = models.TextField("آدرس", blank=True)

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.get_full_name() or self.phone

    @property
    def display_name(self):
        full = self.get_full_name()
        return full if full else self.phone


class PhoneOTP(models.Model):
    """کد یک‌بارمصرف پیامکی برای ورود/ثبت‌نام."""

    phone = models.CharField("شماره موبایل", max_length=11, db_index=True)
    code = models.CharField("کد تایید", max_length=5)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    EXPIRY_SECONDS = 120

    # نشست ۴۷: قبلاً این‌جا `"11111" if True else ...` نوشته شده بود —
    # یعنی صرف‌نظر از این‌که DEBUG چه بود، همیشه همین شاخه اجرا می‌شد؛
    # تبدیل‌شدن به سرویسِ پیامکِ واقعی یک کارِ دستیِ فراموش‌نشدنی (که
    # ممکن بود در production هم فراموش شود) بود، نه یک رفتارِ خودکارِ
    # وابسته به محیط. حالا واقعاً به settings.DEBUG وصل است.
    DEV_FIXED_CODE = "11111"

    @classmethod
    def generate_for(cls, phone: str) -> "PhoneOTP":
        if settings.DEBUG:
            # در محیط توسعه/لوکال (DEBUG=True) کد ثابت صادر می‌شود تا نیاز
            # به سرویس پیامک نباشد — verify_otp هم (در views.py) همین کدِ
            # ثابت را، در همین حالت، از قیدِ منقضی‌شدن/یک‌بارمصرف‌بودن
            # آزاد می‌کند تا در توسعه بشود هر تعداد بار که خواستید با آن
            # وارد شد، بدونِ نیاز به درخواستِ کدِ تازه هر بار.
            code = cls.DEV_FIXED_CODE
        else:
            # TODO: اتصال به سرویس پیامک واقعی (کاوه‌نگار/ملی‌پیامک و ...) و
            # ارسالِ همین code به phone.
            code = f"{random.randint(10000, 99999)}"
        return cls.objects.create(phone=phone, code=code)

    def is_expired(self) -> bool:
        return (timezone.now() - self.created_at).total_seconds() > self.EXPIRY_SECONDS

    def __str__(self):
        return f"{self.phone} - {self.code}"


class Address(models.Model):
    """یک آدرس ذخیره‌شده‌ی «آدرس‌های من» — همان فیلدهایی که فرم
    تسویه‌حساب (apps.orders.forms.CheckoutForm) هم جمع می‌کند، ولی این‌بار
    قابل‌ذخیره و استفاده‌ی مجدد برای خریدهای بعدی. عمداً یک مدل جدا از
    User.address (فیلد قدیمی و موقتِ تک‌آدرسی که همان‌جا هم مستندسازی
    شده بود که قرار است با همین قابلیت جایگزین شود) — یک کاربر می‌تواند
    چند آدرس (خانه، محل کار، ...) داشته باشد.

    این مدل هنوز به CheckoutForm وصل نشده (یعنی انتخاب یکی از این
    آدرس‌ها هنگام تسویه‌حساب هنوز کار نمی‌کند) — این‌جا فقط خودِ صفحه‌ی
    مدیریت آدرس‌ها ساخته شده؛ اتصالش به تسویه‌حساب یک قدم بعدی جداست.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name="کاربر", related_name="addresses", on_delete=models.CASCADE
    )
    title = models.CharField("عنوان آدرس", max_length=50, help_text="مثلاً «خانه» یا «محل کار»")
    full_name = models.CharField("نام و نام خانوادگی تحویل‌گیرنده", max_length=150)
    phone = models.CharField("شماره همراه", max_length=11)
    province = models.CharField("استان", max_length=50)
    city = models.CharField("شهر", max_length=50)
    full_address = models.TextField("آدرس کامل پستی")
    postal_code = models.CharField("کد پستی", max_length=10)
    plaque = models.CharField("پلاک", max_length=20)
    unit = models.CharField("واحد", max_length=20, blank=True)
    is_default = models.BooleanField("آدرس پیش‌فرض", default=False)
    created_at = jmodels.jDateTimeField("تاریخ ثبت", auto_now_add=True)

    class Meta:
        verbose_name = "آدرس"
        verbose_name_plural = "آدرس‌ها"
        ordering = ["-is_default", "-created_at"]

    def __str__(self):
        return f"{self.title} — {self.user}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # فقط یک آدرس پیش‌فرض در هر لحظه، برای هر کاربر — وقتی این یکی
        # پیش‌فرض می‌شود، بقیه‌ی آدرس‌های همین کاربر خودکار از پیش‌فرض
        # بودن خارج می‌شوند. بعد از super().save() انجام می‌شود تا pk
        # همیشه از قبل موجود باشد (برای exclude زیر).
        if self.is_default:
            Address.objects.filter(user_id=self.user_id, is_default=True).exclude(pk=self.pk).update(
                is_default=False
            )