from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView, View
from django.shortcuts import render

from apps.catalog.models import Brand, Category, Product

from .forms import ContactForm
from .models import FAQ, SiteSettings, Testimonial


class IndexView(TemplateView):
    template_name = "store/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_nav"] = "home"
        # بخش «دسته‌بندی‌های محبوب» صفحه‌ی اصلی — فقط دسته‌بندی‌هایی که
        # فروشنده از پنل ادمین صریحاً «دسته‌بندی محبوب» علامت زده (که خودش
        # فقط برای «دسته‌بندی اصلی»ها ممکن است، طبق Category.clean())،
        # حداکثر ۸ تا، دقیقاً طبق خواسته. قبلاً این‌جا همه‌ی دسته‌بندی‌های
        # فعال بدون هیچ سقف/فیلتری نمایش داده می‌شدند.
        context["categories"] = Category.objects.filter(
            is_active=True, is_main_category=True, is_popular=True
        ).order_by("name")[:8]
        context["brands"] = Brand.objects.filter(is_active=True)
        active_products = Product.objects.filter(is_active=True, variants__is_active=True)
        # بخش «محصولات پرفروش» — فقط محصولاتی که فروشنده از لیست محصولات
        # پنل ادمین صریحاً «پرفروش» تیک زده (Product.is_best_seller)،
        # حداکثر ۸ تا. قبلاً این‌جا صرفاً «جدیدترین محصولات» نشان داده
        # می‌شد (order_by("-created_at") بدون هیچ فیلتری) که ربطی به
        # فروش واقعی نداشت.
        context["best_seller_products"] = (
            active_products.filter(is_best_seller=True)
            .select_related("brand", "category")
            .prefetch_related("images", "variants")
            .distinct()
            .order_by("-created_at")[:8]
        )
        # بخش «تخفیفات ویژه و شگفت‌انگیز» — همین‌طور، فقط محصولاتی که
        # فروشنده صریحاً «تخفیف ویژه» تیک زده (Product.is_featured_deal)،
        # حداکثر ۸ تا. قبلاً معیارش صرفاً «حداقل یک تنوع تخفیف‌خورده
        # دارد + جدیدترین» بود، نه انتخاب دستی فروشنده.
        context["featured_deal_products"] = (
            active_products.filter(is_featured_deal=True)
            .select_related("brand", "category")
            .prefetch_related("images", "variants")
            .distinct()
            .order_by("-created_at")[:8]
        )
        context["hero_product"] = self._resolve_hero_product(active_products)
        context["faqs"] = FAQ.objects.filter(is_active=True)
        return context

    def _resolve_hero_product(self, active_products):
        """The hero card's product: whatever the store owner picked in
        SiteSettings.hero_product (see apps/store/models.py), as long as
        it's still active and actually purchasable — otherwise fall back
        to the newest active product overall. Deliberately NOT tied to
        best_seller_products: that list is now curated by the seller and
        can legitimately be empty (e.g. right after upgrading, before
        anything's been marked), and an empty best-sellers list must
        never take the hero card down with it.
        """
        hero_product = SiteSettings.load().hero_product
        if hero_product and hero_product.is_active and hero_product.default_variant:
            return hero_product
        return active_products.order_by("-created_at").first()


class AboutView(TemplateView):
    template_name = "store/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_nav"] = "about"
        context["testimonials"] = Testimonial.objects.filter(is_active=True)
        return context


def robots_txt(request):
    """Plain-text ``robots.txt`` — نشست ۵۲، مرحله‌ی ۳ (گزارشِ نشستِ ۵۱
    گزارش کرده بود این فایل اصلاً وجود نداشت).

    عمداً یک ویوی جنگو است، نه یک فایلِ استاتیک: خطِ ``Sitemap:`` باید
    آدرسِ کاملِ دامنه را داشته باشد، و با ساختنش از روی خودِ
    ``request`` (به‌جای هاردکد‌کردنِ دامنه)، همین یک فایل برای dev/سرورِ
    واقعی/هر دامنه‌ای که بعداً سایت رویش بیاید، درست کار می‌کند — دقیقاً
    همان دلیلی که context_processors.py::seo هم برای canonical_url
    دامنه را از request می‌خواند، نه از یک تنظیمِ ثابت.

    صفحاتِ خصوصی/تراکنشی (پنلِ ادمین، حسابِ کاربری، سبدِ خرید، تسویه‌
    حساب، کدهای تخفیف) از خزیدن مستثنا شده‌اند — این‌ها صفحاتی نیستند
    که بخواهیم در نتیجه‌ی جست‌وجوی گوگل ظاهر شوند.
    """
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /accounts/",
        "Disallow: /cart/",
        "Disallow: /checkout/",
        "Disallow: /coupons/",
        # این یک صفحه نیست، endpoint جنگو برای دراپ‌داونِ جست‌وجوی زنده
        # است (ProductSearchSuggestView) — محتوایی برای ایندکس ندارد.
        "Disallow: /products/search/",
        "",
        f"Sitemap: {request.build_absolute_uri(reverse('sitemap'))}",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


class ContactView(View):
    """GET renders the contact page. POST validates and saves the message
    (viewable/triage-able from the admin as ContactMessage) and redirects
    back with a success message — this form has no email-sending backend
    yet, it just persists messages for staff to review in the admin.
    """

    template_name = "store/contact.html"

    def get(self, request):
        return render(request, self.template_name, {"active_nav": "contact", "form": ContactForm()})

    def post(self, request):
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "پیام شما با موفقیت ارسال شد. به‌زودی با شما تماس می‌گیریم.")
            return redirect("store:contact")
        return render(request, self.template_name, {"active_nav": "contact", "form": form})