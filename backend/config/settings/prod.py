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

# Note: stronger security settings (forced HTTPS, HSTS, etc.) are
# intentionally NOT here yet. Per the roadmap these belong to the
# hardening phase (Phase 6), since they depend on the real Nginx/Coolify
# setup — adding them too early could cause redirect loops or unexpected
# lockouts.