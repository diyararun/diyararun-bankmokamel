from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include

from apps.catalog.sitemaps import ProductSitemap
from apps.store.sitemaps import StaticViewSitemap
from apps.store.views import robots_txt

# نشست ۵۲، مرحله‌ی ۳: sitemap.xml — دو بخش، یکی برای محصولات (که تعدادشان
# زیاد و مرتب در حالِ تغییر است) و یکی برای چند صفحه‌ی ثابتِ سایت.
sitemaps = {
    "products": ProductSitemap,
    "pages": StaticViewSitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("robots.txt", robots_txt, name="robots_txt"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("accounts/", include("apps.accounts.urls")),
    path("cart/", include("apps.cart.urls")),
    path("coupons/", include("apps.coupons.urls")),
    path("products/", include("apps.reviews.urls")),
    path("", include("apps.store.urls")),
]

# Only serve /media/ through Django in development. In production, Nginx
# serves it directly (see docker/nginx/default.conf) — Django/Gunicorn
# never touches media requests there.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)