from django.views.generic import TemplateView

from apps.catalog.models import Brand, Category, Product


class IndexView(TemplateView):
    template_name = "store/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_nav"] = "home"
        context["categories"] = Category.objects.filter(is_active=True)
        context["brands"] = Brand.objects.filter(is_active=True)
        # Newest active products with at least one active variant, for the
        # "featured products" section on the homepage.
        context["featured_products"] = (
            Product.objects.filter(is_active=True, variants__is_active=True)
            .select_related("brand", "category")
            .prefetch_related("images", "variants")
            .distinct()
            .order_by("-created_at")[:8]
        )
        # Products with at least one variant on sale (compare_at_price
        # set), for the "تخفیفات ویژه" slider.
        context["discounted_products"] = (
            Product.objects.filter(
                is_active=True, variants__is_active=True, variants__compare_at_price__isnull=False
            )
            .select_related("brand", "category")
            .prefetch_related("images", "variants")
            .distinct()
            .order_by("-created_at")[:8]
        )
        return context


class AboutView(TemplateView):
    template_name = "store/about.html"

    def get_context_data(self, **kwargs):
        return {**super().get_context_data(**kwargs), "active_nav": "about"}


class ContactView(TemplateView):
    template_name = "store/contact.html"

    def get_context_data(self, **kwargs):
        return {**super().get_context_data(**kwargs), "active_nav": "contact"}