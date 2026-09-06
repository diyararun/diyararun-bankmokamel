import random

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


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

    @classmethod
    def generate_for(cls, phone: str) -> "PhoneOTP":
        # در محیط توسعه کد ثابت ۱۱۱۱۱ صادر می‌شود تا نیاز به سرویس پیامک نباشد.
        # برای اتصال به سرویس پیامک واقعی (کاوه‌نگار/ملی‌پیامک و ...) این متد را
        # جایگزین کنید و ارسال پیامک را در همینجا انجام دهید.
        code = "11111"
        # if True else f"{random.randint(10000, 99999)}" this code for top
        return cls.objects.create(phone=phone, code=code)

    def is_expired(self) -> bool:
        return (timezone.now() - self.created_at).total_seconds() > self.EXPIRY_SECONDS

    def __str__(self):
        return f"{self.phone} - {self.code}"