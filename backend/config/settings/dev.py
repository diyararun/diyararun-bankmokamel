"""
تنظیمات محیط توسعه.

فعال‌سازی: DJANGO_SETTINGS_MODULE=config.settings.dev
(این مقدار پیش‌فرض manage.py/wsgi.py/asgi.py است، پس نیازی به تنظیم
دستی روی سیستم توسعه‌ی شما نیست.)
"""
from .base import *  # noqa: F401,F403

# اگر DEBUG در .env مشخص نشده باشد، در dev پیش‌فرض True است (برخلاف
# base.py که پیش‌فرضش False است — امن‌ترین حالت پیش‌فرض کلی)
DEBUG = env.bool("DEBUG", default=True)

# اگر ALLOWED_HOSTS در .env خالی بود، حداقل روی لوکال کار کند
if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1"]