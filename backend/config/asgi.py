import os
from django.core.asgi import get_asgi_application

# Production overrides this to "config.settings.prod" via docker-compose.prod.yml
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
application = get_asgi_application()