from django import forms

from .models import Brand, Category

SORT_CHOICES = [
    ("newest", "جدیدترین"),
    ("cheapest", "ارزان‌ترین"),
    ("expensive", "گران‌ترین"),
]


class ProductFilterForm(forms.Form):
    """Validates the optional query-string filters on the product list
    page (?category=slug&brand=slug&sort=...). Every field is optional —
    an invalid/missing value just falls back to "no filter" instead of
    raising an error, since these are plain GET params a visitor could
    type or bookmark by hand, not a form they submit and must get right.
    """

    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True), to_field_name="slug", required=False
    )
    brand = forms.ModelChoiceField(
        queryset=Brand.objects.filter(is_active=True), to_field_name="slug", required=False
    )
    sort = forms.ChoiceField(choices=SORT_CHOICES, required=False)

    def clean_sort(self):
        # Falls back to "newest" for both a blank value and an invalid one
        # (ChoiceField already rejects invalid values in full_clean, but
        # since required=False that only fires when non-empty and invalid;
        # is_valid() would be False then, and callers already treat an
        # invalid form the same as "no filters" — see ProductListView).
        return self.cleaned_data.get("sort") or "newest"
