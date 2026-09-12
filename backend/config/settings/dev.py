"""
Development environment settings.

Activated via: DJANGO_SETTINGS_MODULE=config.settings.dev
(this is already the default in manage.py/wsgi.py/asgi.py, so no manual
setup is needed on your development machine.)
"""
from .base import *  # noqa: F401,F403

# Defaults to True in dev if DEBUG isn't set in .env (unlike base.py,
# whose default is False — the safest default overall).
DEBUG = env.bool("DEBUG", default=True)

# Fall back to localhost if ALLOWED_HOSTS is empty in .env
if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1"]