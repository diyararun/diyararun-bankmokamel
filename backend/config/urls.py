from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("apps.accounts.urls")),
    path("cart/", include("apps.cart.urls")),
    path("products/", include("apps.reviews.urls")),
    path("", include("apps.store.urls")),
]

# Only serve /media/ through Django in development. In production, Nginx
# serves it directly (see docker/nginx/default.conf) — Django/Gunicorn
# never touches media requests there.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)