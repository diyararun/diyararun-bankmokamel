"""
تنظیمات محیط تولید (production).

فعال‌سازی: DJANGO_SETTINGS_MODULE=config.settings.prod
(این مقدار در docker-compose.prod.yml به‌صورت صریح ست شده است.)
"""
from .base import *  # noqa: F401,F403

DEBUG = False

# در production نباید ALLOWED_HOSTS خالی باشد؛ خالی گذاشتنش عمداً باعث
# خطا می‌شود تا با تنظیمات ناقص/فراموش‌شده دیپلوی نکنیم.
if not ALLOWED_HOSTS:
    raise ValueError("ALLOWED_HOSTS must be set via the .env file in production")

# محل واقعی فایل‌های build‌شده‌ی فرانت (توسط مرحله‌ی frontend-builder در
# Dockerfile ساخته می‌شود) — رفع همان باگ قبلی STATICFILES_DIRS
STATICFILES_DIRS = [BASE_DIR.parent / "frontend" / "dist"]

# نکته: تنظیمات امنیتی سطح‌بالاتر (HTTPS اجباری، HSTS و ...) عمداً اینجا
# نیستند — طبق نقشه راه، این‌ها در فاز سخت‌سازی (فاز ۶) اضافه می‌شوند،
# چون به تنظیمات Nginx/Coolify واقعی سرور نیاز دارند و زودتر از موعد
# اضافه‌کردنشان می‌تواند باعث ریدایرکت‌لوپ یا قفل‌شدن غیرمنتظره بشود.