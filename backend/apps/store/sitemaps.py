"""XML sitemap entry for the handful of site pages that aren't backed
by a model — نشست ۵۲، مرحله‌ی ۳. Product pages have their own,
model-driven sitemap (apps/catalog/sitemaps.py::ProductSitemap).
"""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse

# هر صفحه چقدر زود عوض می‌شود و چقدر برای ایندکس اهمیت دارد — صفحه‌ی
# اصلی و لیستِ محصولات (که هر دو محتوایشان مرتب تغییر می‌کند: محصولاتِ
# پرفروش/تخفیف‌دار، موجودی) نسبت به «درباره ما»/«تماس با ما» (که ماه‌ها
# دست‌نخورده می‌مانند) هم زودتر باید دوباره خزیده شوند هم اولویتِ
# بالاتری دارند.
_PAGE_META = {
    "store:index": {"changefreq": "daily", "priority": 1.0},
    "store:products": {"changefreq": "daily", "priority": 0.9},
    "store:about": {"changefreq": "monthly", "priority": 0.5},
    "store:contact": {"changefreq": "monthly", "priority": 0.5},
}


class StaticViewSitemap(Sitemap):
    def items(self):
        return list(_PAGE_META.keys())

    def location(self, item):
        return reverse(item)

    def changefreq(self, item):
        return _PAGE_META[item]["changefreq"]

    def priority(self, item):
        return _PAGE_META[item]["priority"]
