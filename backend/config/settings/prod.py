"""
Production environment settings.

Activated via: DJANGO_SETTINGS_MODULE=config.settings.prod
(explicitly set in docker-compose.prod.yml.)
"""
from .base import *  # noqa: F401,F403

DEBUG = False

# ALLOWED_HOSTS must never be empty in production; failing loudly here
# prevents deploying with an incomplete/forgotten .env file.
if not ALLOWED_HOSTS:
    raise ValueError("ALLOWED_HOSTS must be set via the .env file in production")

# Real location of the built frontend assets (produced by the
# frontend-builder stage in the Dockerfile) — fixes the earlier
# STATICFILES_DIRS bug.
STATICFILES_DIRS = [BASE_DIR.parent / "frontend" / "dist"]

# نشست ۵۵: اولین دیپلویِ واقعی روی Coolify، لاگین به /admin/ با ارورِ
# "403 Forbidden — CSRF verification failed" مواجه شد. این ربطی به
# models.py یا هر کدِ اپلیکیشن ندارد — دقیقاً همان چیزی است که کامنتِ
# قبلیِ همین فایل از قبل پیش‌بینی کرده بود ("این‌ها به‌خاطرِ اینکه به
# Nginx/Coolifyِ واقعی نیاز دارند این‌جا نبودند").
#
# دلیلِ فنی: جنگو از نسخه‌ی ۴ به بعد، برایِ هر درخواستِ POST که از یک
# دامنه‌یِ HTTPS می‌آید (مثلِ فرمِ لاگینِ ادمین)، هدرِ Origin/Referer را
# با CSRF_TRUSTED_ORIGINS مقایسه می‌کند — و برخلافِ ALLOWED_HOSTS، این‌جا
# باید scheme (یعنی "https://") هم صراحتاً نوشته شود، نه فقط نامِ دامنه.
# چون این تنظیم اصلاً وجود نداشت، جنگو هیچ originای را معتبر نمی‌دانست
# و لاگینِ ادمین را رد می‌کرد.
CSRF_TRUSTED_ORIGINS = [
    f"https://{host}" for host in ALLOWED_HOSTS if host not in ("localhost", "127.0.0.1")
]

# دلیلِ دومِ مرتبط: Coolify از طریقِ Traefik (پراکسیِ داخلی‌اش) کار
# می‌کند — یعنی HTTPS واقعی بینِ مرورگرِ کاربر و Traefik بسته می‌شود، و
# از آن‌جا به بعد (بینِ Traefik و کانتینرِ خودِ ما) فقط HTTP معمولی رد و
# بدل می‌شود. بدونِ این خط، جنگو فکر می‌کند خودِ درخواست هیچ‌وقت HTTPS
# نبوده (چون از دیدِ خودِ کانتینر همین‌طور است)، که هم روی رفتارِ CSRF و
# هم روی هر جای دیگری که از request.is_secure() یا
# request.build_absolute_uri() استفاده می‌کند (مثلاً canonical_url در
# نشستِ ۵۲) اثر می‌گذارد. این خط به جنگو می‌گوید هدرِ استانداردِ
# X-Forwarded-Proto را که Traefik ست می‌کند، معتبر بداند.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# نکته: بقیه‌ی سخت‌گیری‌های امنیتی (HSTS، اجبارِ HTTPS، کوکی‌های Secure
# و غیره) هنوز عمداً اضافه نشده‌اند — طبقِ همان کامنتِ قبلی، آن‌ها فازِ
# سخت‌گیریِ کاملِ بعدی هستند. این دو خط فقط همان حداقلی است که همین
# الان برای کارکردنِ لاگینِ ادمین پشتِ Coolify لازم بود.