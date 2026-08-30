"""
تنظیمات مشترک پروژه جنگو - بانک مکمل

این فایل مستقیماً اجرا نمی‌شود. dev.py و prod.py هرکدام با
"from .base import *" این فایل را وارد می‌کنند و فقط تفاوت‌های
محیط خودشان (DEBUG، ALLOWED_HOSTS و ...) را روی آن اضافه/رونویسی می‌کنند.
"""
from pathlib import Path

import environ

# این فایل الان داخل config/settings/base.py است، پس برای رسیدن به ریشه‌ی
# backend/ باید سه پله بالا برویم: base.py -> settings/ -> config/ -> backend/
BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()

# فایل .env در ریشه‌ی مخزن (کنار backend/ و frontend/) قرار دارد.
# داخل کانتینر Docker این فایل اصلاً وجود ندارد (در .dockerignore است)؛
# مقادیر آنجا از طریق "env_file" در docker-compose مستقیم به عنوان
# متغیر محیطی واقعی تزریق می‌شوند، پس read_env() به‌سادگی کاری نمی‌کند
# و از همان متغیرهای محیطی موجود استفاده می‌شود.
environ.Env.read_env(str(BASE_DIR.parent / ".env"))

SECRET_KEY = env("SECRET_KEY")
DEBUG = env.bool("DEBUG", default=False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_vite",
    "django_jalali",

    #apps
    "accounts",
    "store",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # سبد خرید و بج آن در همه‌ی صفحات در دسترس باشد
                "store.context_processors.cart",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# پایگاه‌داده همیشه PostgreSQL است (حتی در dev) تا رفتار محیط توسعه با
# production یکسان باشد و باگ‌های مخصوص یک دیتابیس دیر کشف نشوند.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB"),
        "USER": env("POSTGRES_USER"),
        "PASSWORD": env("POSTGRES_PASSWORD"),
        "HOST": env("POSTGRES_HOST"),
        "PORT": env("POSTGRES_PORT"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
]

AUTH_USER_MODEL = "accounts.User"

# ==================== فارسی‌سازی ====================
# "fa-ir" دقیق‌تر از "fa" است (فارسیِ ایران)؛ جنگو در نبود ترجمه‌ی
# اختصاصی fa-ir به‌صورت خودکار روی کاتالوگ عمومی fa بازمی‌گردد، پس هیچ
# ترجمه‌ای از دست نمی‌رود. همین مقدار باعث راست‌چین و فارسی‌شدن خودکار
# پنل ادمین پیش‌فرض جنگو هم می‌شود.
LANGUAGE_CODE = "fa-ir"
TIME_ZONE = "Asia/Tehran"
USE_I18N = True
USE_TZ = True

# اعداد را با جداکننده‌ی هزارگان نمایش بده (مثلاً در قیمت محصولات در ادمین)
USE_THOUSAND_SEPARATOR = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
# توجه: STATICFILES_DIRS اینجا نیست! فقط در prod.py تعریف می‌شود چون به
# پوشه‌ی خروجی build فرانت (frontend/dist) اشاره می‌کند که در حالت dev
# اصلاً وجود ندارد (چون به Vite dev server وصل می‌شویم، نه فایل build شده).

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ==================== ورود / خروج ====================
LOGIN_URL = "accounts:auth"
LOGIN_REDIRECT_URL = "store:index"
LOGOUT_REDIRECT_URL = "store:index"

# ==================== django-vite ====================
# در حالت توسعه (npm run dev) به سرور Vite وصل می‌شود
# در حالت production از manifest.json خروجی build استفاده می‌کند
DJANGO_VITE = {
    "default": {
        "dev_mode": DEBUG,
        "dev_server_port": 5173,
        "manifest_path": BASE_DIR.parent / "frontend" / "dist" / ".vite" / "manifest.json",
        "static_url_prefix": "",
    }
}

# ==================== کش (برای django-ratelimit) ====================
# LocMemCache برای شروع کافی است، اما حافظه‌اش per-process است؛ یعنی در
# production با چند worker گانیکورن، هر worker محدودیت درخواست را جدا
# می‌شمارد (محدودیت واقعی، مجموع تمام workerهاست). وقتی طبق نقشه راه
# Redis را اضافه کردیم، این بخش باید به آن سوییچ شود.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}