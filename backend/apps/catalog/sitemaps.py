"""XML sitemap entries for catalog pages — نشست ۵۲، مرحله‌ی ۳ از
گزارشِ سئوی نشستِ ۵۱ (که گزارش کرده بود کلِ پروژه هیچ sitemap.xml‌ای
نداشت، یعنی گوگل صفحاتِ محصول را فقط از طریقِ لینک‌های داخلیِ سایت
پیدا می‌کرد، نه با یک فهرستِ صریح).
"""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Product


class ProductSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Product.objects.filter(is_active=True).order_by("-updated_at")

    def lastmod(self, product):
        """``Product.updated_at`` یک ``jDateTimeField`` است — یعنی
        ``jdatetime.datetime`` برمی‌گرداند، نه ``datetime.datetime``ی
        استاندارد. رندرِ ``sitemap.xml`` برای تگِ ``<lastmod>`` از فیلترِ
        ``|date`` خودِ جنگو استفاده می‌کند که دقیقاً همان چیزی است که در
        نشست ۴۵ باعثِ کرشِ
        ``combine() argument 1 must be datetime.date, not datetime`` شد
        (رجوع کنید به ``Order.reservation_deadline_ts`` در
        ``apps/orders/models.py``). همان راه‌حل این‌جا هم تکرار شده: قبل
        از تحویل به sitemap framework، به‌صراحت به یک تاریخِ میلادیِ
        استاندارد تبدیل می‌شود.
        """
        updated = product.updated_at
        to_gregorian = getattr(updated, "togregorian", None)
        return to_gregorian() if to_gregorian is not None else updated

    def location(self, product):
        return reverse("store:product_detail", kwargs={"slug": product.slug})
