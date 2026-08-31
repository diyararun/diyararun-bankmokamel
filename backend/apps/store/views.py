from django.views.generic import TemplateView

from apps.catalog.models import Product


class IndexView(TemplateView):
    template_name = "pages/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_nav"] = "home"
        # Newest active products with at least one active variant, for the
        # "featured products" section on the homepage.
        context["featured_products"] = (
            Product.objects.filter(is_active=True, variants__is_active=True)
            .select_related("brand", "category")
            .prefetch_related("images", "variants")
            .distinct()
            .order_by("-created_at")[:8]
        )
        return context


class AboutView(TemplateView):
    template_name = "pages/about.html"

    def get_context_data(self, **kwargs):
        return {**super().get_context_data(**kwargs), "active_nav": "about"}


class ContactView(TemplateView):
    template_name = "pages/contact.html"

    def get_context_data(self, **kwargs):
        return {**super().get_context_data(**kwargs), "active_nav": "contact"}


class CheckoutView(TemplateView):
    template_name = "pages/checkout.html"

    def get_context_data(self, **kwargs):
        return {**super().get_context_data(**kwargs), "active_nav": "checkout"}