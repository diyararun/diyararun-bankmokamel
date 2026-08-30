import os
from django.core.wsgi import get_wsgi_application

# Production overrides this to "config.settings.prod" via docker-compose.prod.yml
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
application = get_wsgi_application()