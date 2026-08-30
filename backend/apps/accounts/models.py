import random

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """
    کاربر بر اساس شماره موبایل (متناسب با فرم ورود/ثبت‌نام پیامکی سایت).
    username همچنان برای سازگاری با django.contrib.auth نگه داشته شده
    ولی مقدار آن همان شماره موبایل است.
    """

    phone = models.CharField("شماره موبایل", max_length=11, unique=True)
    national_code = models.CharField("کد ملی", max_length=10, blank=True)
    avatar_emoji = models.CharField("آیکون پروفایل", max_length=4, default="👤")

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

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

    @classmethod
    def generate_for(cls, phone: str) -> "PhoneOTP":
        # در محیط توسعه کد ثابت ۱۱۱۱۱ صادر می‌شود تا نیاز به سرویس پیامک نباشد.
        # برای اتصال به سرویس پیامک واقعی (کاوه‌نگار/ملی‌پیامک و ...) این متد را
        # جایگزین کنید و ارسال پیامک را در همینجا انجام دهید.
        code = "11111" if True else f"{random.randint(10000, 99999)}"
        return cls.objects.create(phone=phone, code=code)

    def is_expired(self) -> bool:
        return (timezone.now() - self.created_at).total_seconds() > self.EXPIRY_SECONDS

    def __str__(self):
        return f"{self.phone} - {self.code}"
