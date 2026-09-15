from django import forms

from .models import Brand, Category, Product

SORT_CHOICES = [
    ("newest", "جدیدترین"),
    ("cheapest", "ارزان‌ترین"),
    ("expensive", "گران‌ترین"),
]

# (value, label, min_grams, max_grams) — max_grams=None means "and above".
# Matches the four weight buttons in the products.html sidebar exactly.
WEIGHT_RANGE_CHOICES = [
    ("under_1kg", "زیر ۱ کیلوگرم", 0, 1000),
    ("1_2kg", "۱ تا ۲ کیلوگرم", 1000, 2000),
    ("2_4kg", "۲ تا ۴ کیلوگرم", 2000, 4000),
    ("over_4kg", "بالای ۴ کیلوگرم", 4000, None),
]


class ProductFilterForm(forms.Form):
    """Validates every optional query-string filter on the product list
    page (?brand=on&brand=bsn&price_max=...&weight_range=...&form_type=powder&in_stock_only=1&sort=...).
    Every field is optional — an invalid/missing value just falls back to
    "no filter" instead of raising an error, since these are plain GET
    params a visitor could type or bookmark by hand, not a form they
    submit and must get exactly right.
    """

    # Free-text search coming from the header's live-search box (?q=...).
    # Matched against product/brand/category name — see
    # ProductListView.get_queryset for how it's applied.
    q = forms.CharField(required=False, max_length=200)
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True), to_field_name="slug", required=False
    )
    # Multiple brands (checkboxes in the sidebar) — matches the mockup,
    # unlike the old single-brand version.
    brand = forms.ModelMultipleChoiceField(
        queryset=Brand.objects.filter(is_active=True), to_field_name="slug", required=False
    )
    price_max = forms.IntegerField(required=False, min_value=0)
    weight_range = forms.ChoiceField(
        choices=[(value, label) for value, label, _min, _max in WEIGHT_RANGE_CHOICES],
        required=False,
    )
    form_type = forms.MultipleChoiceField(choices=Product.FORM_TYPE_CHOICES, required=False)
    in_stock_only = forms.BooleanField(required=False)
    sort = forms.ChoiceField(choices=SORT_CHOICES, required=False)

    def clean_sort(self):
        return self.cleaned_data.get("sort") or "newest"

    def clean_q(self):
        return self.cleaned_data.get("q", "").strip()