from django.views.generic import DetailView, ListView

from apps.reviews.forms import ReviewForm

from .forms import WEIGHT_RANGE_CHOICES, ProductFilterForm
from .models import Brand, Category, Flavor, Product

SORT_FIELD_MAP = {
    "newest": "-created_at",
    "cheapest": "variants__price",
    "expensive": "-variants__price",
}


class ProductListView(ListView):
    model = Product
    template_name = "catalog/products.html"
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

        if not self.filter_form.is_valid():
            # An unrecognized value anywhere just means "show everything"
            # rather than a hard error — these are bookmarkable GET
            # params, not a form a visitor fills in and must get exactly
            # right.
            return queryset.order_by("-created_at").distinct()

        data = self.filter_form.cleaned_data

        if data.get("category"):
            queryset = queryset.filter(category=data["category"])
        if data.get("brand"):
            queryset = queryset.filter(brand__in=data["brand"])
        if data.get("form_type"):
            queryset = queryset.filter(form_type__in=data["form_type"])
        if data.get("price_max"):
            queryset = queryset.filter(variants__price__lte=data["price_max"])
        if data.get("weight_range"):
            for value, _label, min_g, max_g in WEIGHT_RANGE_CHOICES:
                if value == data["weight_range"]:
                    queryset = queryset.filter(variants__weight_grams__gte=min_g)
                    if max_g is not None:
                        queryset = queryset.filter(variants__weight_grams__lt=max_g)
                    break
        if data.get("in_stock_only"):
            queryset = queryset.filter(variants__stock__gt=0, variants__is_active=True)

        sort = data.get("sort") or "newest"
        return queryset.order_by(SORT_FIELD_MAP.get(sort, "-created_at")).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_nav"] = "products"
        context["categories"] = Category.objects.filter(is_active=True)
        context["brands"] = Brand.objects.filter(is_active=True)
        context["weight_ranges"] = [(v, label) for v, label, _min, _max in WEIGHT_RANGE_CHOICES]
        context["form_types"] = Product.FORM_TYPE_CHOICES

        # Used by pagination links (?{{ querystring }}&page=N) so changing
        # page never drops the current filters/sort.
        querydict = self.request.GET.copy()
        querydict.pop("page", None)
        context["querystring"] = querydict.urlencode()

        if self.filter_form.is_valid():
            data = self.filter_form.cleaned_data
            context["current_sort"] = data.get("sort") or "newest"
            context["selected_brand_slugs"] = [b.slug for b in data.get("brand") or []]
            context["selected_form_types"] = data.get("form_type") or []
            context["selected_weight_range"] = data.get("weight_range") or ""
            context["selected_price_max"] = data.get("price_max")
            context["selected_in_stock_only"] = data.get("in_stock_only")
        else:
            context["current_sort"] = "newest"
            context["selected_brand_slugs"] = []
            context["selected_form_types"] = []
            context["selected_weight_range"] = ""
            context["selected_price_max"] = None
            context["selected_in_stock_only"] = False
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = "catalog/product_detail.html"
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
        context["review_form"] = ReviewForm()
        # Distinct flavors among this product's active variants, for the
        # flavor-picker buttons. Combining a selected flavor with the
        # matching weight/serving variant is a frontend JS job (like
        # cartDrawer.js) — the backend just provides all the raw data.
        context["flavors"] = Flavor.objects.filter(
            variants__product=product, variants__is_active=True
        ).distinct()
        context["related_products"] = (
            Product.objects.filter(is_active=True, category=product.category)
            .exclude(pk=product.pk)
            .select_related("brand")
            .prefetch_related("images", "variants")[:4]
        )
        default_variant = product.default_variant
        context["product_json"] = {
            "name": product.name,
            "images": [img.image.url for img in product.images.all()],
            "defaultVariantId": default_variant.id if default_variant else None,
            "defaultVariantPrice": default_variant.price if default_variant else 0,
            # Full variant list so the weight/serving picker can switch the
            # selected variant (and its price/stock) on the client without
            # a page reload — matching the flavor-picker's own docstring
            # above: "the backend just provides all the raw data."
            "variants": [
                {
                    "id": v.id,
                    "label": v.label,
                    "price": v.price,
                    "compareAtPrice": v.compare_at_price,
                    "inStock": v.is_in_stock,
                    # None for variants with no flavor set — the flavor
                    # picker only renders when a product HAS flavors at
                    # all, but not every variant of a flavored product is
                    # guaranteed to have one assigned.
                    "flavorId": v.flavor_id,
                }
                for v in product.active_variants
            ],
        }
        return context