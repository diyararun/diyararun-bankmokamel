"""
Shared settings for the Django project - BankMokamel supplement store.

This file is never used directly. dev.py and prod.py both import it with
"from .base import *" and only add/override the differences for their
own environment (DEBUG, ALLOWED_HOSTS, etc.) on top of it.
"""
from pathlib import Path

import environ

# This file lives at config/settings/base.py, so reaching the backend/ root
# needs three levels up: base.py -> settings/ -> config/ -> backend/
BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()

# The .env file lives at the repository root (next to backend/ and
# frontend/). Inside a Docker container this file doesn't exist at all
# (it's excluded via .dockerignore); those same values are injected
# directly as real environment variables through docker-compose's
# "env_file" option, so read_env() simply does nothing there and the
# existing environment variables are used instead.
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
    "apps.accounts",
    "apps.catalog",
    "apps.reviews",
    "apps.cart",
    "apps.orders",
    "apps.store",
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
                # Makes the cart and its badge available on every page
                "apps.store.context_processors.cart",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# The database is always PostgreSQL, even in dev, so the development
# environment behaves the same as production and database-specific bugs
# don't surface late.
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

# ==================== Localization (Persian) ====================
# "fa-ir" is more precise than "fa" (Persian as spoken in Iran). Django
# automatically falls back to the generic "fa" catalog when no dedicated
# "fa-ir" translation exists, so no translations are lost. This same
# value is also what makes Django's default admin panel RTL and Persian
# automatically.
LANGUAGE_CODE = "fa-ir"
TIME_ZONE = "Asia/Tehran"
USE_I18N = True
USE_TZ = True

# Show numbers with a thousands separator (e.g. product prices in the admin)
USE_THOUSAND_SEPARATOR = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
# Note: STATICFILES_DIRS is intentionally NOT defined here! It's only set
# in prod.py, because it points at the frontend build output
# (frontend/dist), which doesn't exist in dev mode (we connect to the
# live Vite dev server instead of a pre-built file there).

# User-uploaded files (product images, brand logos, etc.)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ==================== Login / logout ====================
LOGIN_URL = "accounts:auth"
LOGIN_REDIRECT_URL = "store:index"
LOGOUT_REDIRECT_URL = "store:index"

# ==================== django-vite ====================
# In development (npm run dev) this connects to the live Vite dev server.
# In production it reads the manifest.json produced by the build instead.
DJANGO_VITE = {
    "default": {
        "dev_mode": DEBUG,
        "dev_server_port": 5173,
        "manifest_path": BASE_DIR.parent / "frontend" / "dist" / ".vite" / "manifest.json",
        "static_url_prefix": "",
    }
}

# ==================== Cache (used by django-ratelimit) ====================
# LocMemCache is fine to start with, but its memory is per-process — so in
# production, with multiple Gunicorn workers, each worker counts rate
# limits separately (the real effective limit is the sum across all
# workers). Once Redis is added per the roadmap, this should switch to it.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}