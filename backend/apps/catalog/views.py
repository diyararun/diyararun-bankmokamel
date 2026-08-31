from django.views.generic import DetailView, ListView

from .forms import ProductFilterForm
from .models import Brand, Category, Product

SORT_FIELD_MAP = {
    "newest": "-created_at",
    "cheapest": "variants__price",
    "expensive": "-variants__price",
}


class ProductListView(ListView):
    model = Product
    template_name = "pages/products.html"
    context_object_name = "products"
    paginate_by = 9  # matches the template's copy ("۱ تا ۹ از ...")

    def get_queryset(self):
        # Stored on self so get_context_data() can reuse the same
        # validated data without re-parsing request.GET a second time.
        self.filter_form = ProductFilterForm(self.request.GET)

        queryset = (
            Product.objects.filter(is_active=True)
            .select_related("brand", "category")
            .prefetch_related("images", "variants")
        )

        if self.filter_form.is_valid():
            category = self.filter_form.cleaned_data.get("category")
            brand = self.filter_form.cleaned_data.get("brand")
            sort = self.filter_form.cleaned_data.get("sort") or "newest"
            if category:
                queryset = queryset.filter(category=category)
            if brand:
                queryset = queryset.filter(brand=brand)
        else:
            # An unrecognized ?sort=... or a slug that doesn't match any
            # active category/brand just means "show everything" rather
            # than a hard error — these are bookmarkable GET params, not
            # a form a visitor fills in and must get exactly right.
            sort = "newest"

        return queryset.order_by(SORT_FIELD_MAP.get(sort, "-created_at")).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_nav"] = "products"
        context["categories"] = Category.objects.filter(is_active=True)
        context["brands"] = Brand.objects.filter(is_active=True)
        context["current_sort"] = (
            self.filter_form.cleaned_data.get("sort") or "newest" if self.filter_form.is_valid() else "newest"
        )
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = "pages/product_detail.html"
    context_object_name = "product"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related("brand", "category").prefetch_related(
            "images", "variants__flavor", "specs", "reviews__user"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_nav"] = "products"
        product = self.object
        context["reviews"] = product.reviews.filter(is_approved=True).select_related("user")
        context["related_products"] = (
            Product.objects.filter(is_active=True, category=product.category)
            .exclude(pk=product.pk)
            .select_related("brand")
            .prefetch_related("images", "variants")[:4]
        )
        return context