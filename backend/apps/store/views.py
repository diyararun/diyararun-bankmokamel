from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import TemplateView, View
from django.shortcuts import render

from apps.catalog.models import Brand, Category, Product

from .forms import ContactForm
from .models import Testimonial


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
        context = super().get_context_data(**kwargs)
        context["active_nav"] = "about"
        context["testimonials"] = Testimonial.objects.filter(is_active=True)
        return context


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