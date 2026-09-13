from django.db.models import Max, Min, Q
from django.http import JsonResponse
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView, ListView

from apps.reviews.forms import ReviewForm

from .forms import WEIGHT_RANGE_CHOICES, ProductFilterForm
from .models import Brand, Category, Flavor, Product, ProductVariant

# Fallback price-slider bounds (تومان) for the rare case where there are no
# active variants at all yet (a brand-new store with an empty catalog) — a
# hardcoded range that only ever gets *used* when there's no real data to
# derive one from, unlike the old always-hardcoded 500,000–6,000,000.
FALLBACK_PRICE_MIN = 0
FALLBACK_PRICE_MAX = 10_000_000

# Max number of live-search suggestions returned by ProductSearchSuggestView
# — a dropdown, not a results page, so this stays intentionally small.
SEARCH_SUGGESTION_LIMIT = 6


def _search_filter(q):
    """Shared "does this product match the search text" condition, used by
    both the live-search dropdown (ProductSearchSuggestView) and the full
    product list page's ?q= filter (ProductListView) — so typing the same
    text into either one finds the same products.
    """
    return (
        Q(name__icontains=q)
        | Q(short_description__icontains=q)
        | Q(brand__name__icontains=q)
        | Q(category__name__icontains=q)
    )


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

        if data.get("q"):
            queryset = queryset.filter(_search_filter(data["q"]))
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

        # Price-slider bounds, computed from real data instead of a
        # hardcoded 500,000–6,000,000: otherwise a new product priced
        # above whatever number was hardcoded couldn't be reached by the
        # slider at all, and — worse — its default position would submit
        # that stale max as price_max on every filter submit, silently
        # hiding any product above it even when the seller never touched
        # the price filter.
        active_variant_prices = ProductVariant.objects.filter(is_active=True).aggregate(
            min_price=Min("price"), max_price=Max("price")
        )
        context["price_min"] = active_variant_prices["min_price"] or FALLBACK_PRICE_MIN
        context["price_max_bound"] = active_variant_prices["max_price"] or FALLBACK_PRICE_MAX

        # These two filter sections are only worth showing if the current
        # catalog actually varies along that dimension — a fixed set of
        # weight buckets or form-type checkboxes is confusing/useless if
        # every product (or none) has a value for it. See the template
        # for the {% if %} that uses these.
        context["show_weight_filter"] = ProductVariant.objects.filter(
            is_active=True, weight_grams__isnull=False
        ).exists()
        context["show_form_type_filter"] = Product.objects.filter(is_active=True).exclude(form_type="").exists()

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
            context["search_query"] = data.get("q") or ""
        else:
            context["current_sort"] = "newest"
            context["selected_brand_slugs"] = []
            context["selected_form_types"] = []
            context["selected_weight_range"] = ""
            context["selected_price_max"] = None
            context["selected_in_stock_only"] = False
            context["search_query"] = ""
        return context


class ProductSearchSuggestView(View):
    """Backs the header's live-search box: GET /products/search/?q=...
    returns a small JSON list of matching products (name, url, image,
    brand, price) for the dropdown that appears while typing.

    Deliberately a plain View (not DRF) — same choice already made for the
    rest of this project (see the session log: "no DRF"). A handful of
    fields as JsonResponse doesn't need a serializer framework.
    """

    def get(self, request):
        q = request.GET.get("q", "").strip()
        if len(q) < 2:
            # Avoid a near-full-table scan on a single stray keystroke —
            # the frontend also debounces, this is the backend's own floor.
            return JsonResponse({"results": []})

        products = (
            Product.objects.filter(is_active=True, variants__is_active=True)
            .filter(_search_filter(q))
            .select_related("brand")
            .prefetch_related("images", "variants")
            .distinct()
            .order_by("-created_at")[:SEARCH_SUGGESTION_LIMIT]
        )

        results = []
        for product in products:
            image = product.images.first()
            variant = product.default_variant
            results.append(
                {
                    "name": product.name,
                    "brand": product.brand.name if product.brand_id else "",
                    "url": reverse("store:product_detail", kwargs={"slug": product.slug}),
                    "image": image.image.url if image else "",
                    "price": variant.price if variant else None,
                }
            )
        return JsonResponse({"results": results})


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
        context["related_products"] = self._related_products(product)
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

    # Pool size for _related_products below: how many same-category
    # candidates get pulled from the DB before ranking narrows them down
    # to RELATED_PRODUCTS_LIMIT. Bounded on purpose — ranking the entire
    # category in Python instead of a fixed-size pool would turn a big
    # category into an unbounded amount of work per page view.
    RELATED_PRODUCTS_POOL_SIZE = 20
    RELATED_PRODUCTS_LIMIT = 4

    def _related_products(self, product):
        """Same-category products, ranked by how close a fit they are to
        the one being viewed — previously this was just "same category,
        newest first," which could easily surface something only
        superficially related (different brand, wildly different price)
        ahead of a genuinely comparable alternative.

        Ranking, most to least important:
        1. Same brand first — a shopper looking at one برند's product is
           plausibly shopping that brand's other products too.
        2. Closest price to the current product's — something priced
           nothing like what they're looking at isn't a realistic
           swap-in alternative, whichever brand it's from.
        3. Newest first, as a final tiebreaker (the previous behavior),
           preserved implicitly: `sorted()` is stable, and the pool
           below is already fetched in that order.

        Ranked in Python rather than a single `.order_by()` because a
        product's effective price (`default_variant.price`) isn't a
        plain DB column — it's "cheapest in-stock variant, or cheapest
        overall" (see Product.default_variant) — so comparing prices
        directly in the database would mean duplicating that logic as
        raw SQL. Ranking a bounded pool of RELATED_PRODUCTS_POOL_SIZE
        candidates in Python instead keeps this simple at the cost of
        one query per candidate for its default_variant (acceptable at
        this pool size; the same trade-off products.html and index.html
        already make calling p.default_variant per card in a loop).

        Returns an empty list/queryset if the product's category has no
        other active products at all — the template hides the whole
        "محصولات مرتبط" section in that case rather than showing it
        with nothing (or a placeholder) inside.
        """
        current_variant = product.default_variant
        current_price = current_variant.price if current_variant else None

        candidates = (
            Product.objects.filter(is_active=True, category=product.category)
            .exclude(pk=product.pk)
            .select_related("brand")
            .prefetch_related("images", "variants")
            .order_by("-created_at")[: self.RELATED_PRODUCTS_POOL_SIZE]
        )

        def rank_key(candidate):
            same_brand = candidate.brand_id == product.brand_id
            candidate_variant = candidate.default_variant
            if current_price is not None and candidate_variant is not None:
                price_gap = abs(candidate_variant.price - current_price)
            else:
                # Nothing to compare prices against — don't let this
                # axis arbitrarily favor one candidate over another.
                price_gap = 0
            return (not same_brand, price_gap)

        return sorted(candidates, key=rank_key)[: self.RELATED_PRODUCTS_LIMIT]
