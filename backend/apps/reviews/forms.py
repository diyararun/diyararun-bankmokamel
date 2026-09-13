from django import forms

from .models import Review

# Highest first, so the radio buttons read top-to-bottom the way a star
# picker would (5 stars first).
RATING_CHOICES = [(i, "★" * i) for i in range(5, 0, -1)]


class ReviewForm(forms.ModelForm):
    """Matches the product page's "دیدگاه خود را بنویسید" form. Only
    rating + comment: no name/email fields, since the reviewer is the
    logged-in user (see ReviewCreateView) — the mockup's name/email
    inputs assumed no login system, which doesn't match this project.

    `rating`'s widget (RadioSelect) is never actually rendered by
    {{ review_form.rating }} on the product page — the template hand-
    writes 5 clickable star icons instead (see product_detail.html and
    productDetail.js) for a much better picking experience than 5 plain
    radio-button dots. They still post to the same "rating" field name
    with the same 1-5 values, so this field's validation (a real
    ChoiceField, checked against RATING_CHOICES) is exactly as strict as
    if the default widget were used — only the visual presentation
    differs. RadioSelect is kept here mainly so this field still makes
    sense if ReviewForm is ever rendered generically somewhere else.
    """

    rating = forms.ChoiceField(choices=RATING_CHOICES, label="امتیاز", widget=forms.RadioSelect)

    class Meta:
        model = Review
        fields = ["rating", "comment"]
        labels = {"comment": "متن دیدگاه"}
        widgets = {
            "comment": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "تجربه استفاده خود از این محصول را بنویسید...",
                    "class": "w-full p-2.5 bg-white rounded-xl border border-slate-200 text-xs focus:outline-none focus:ring-2 focus:ring-red-600",
                }
            ),
        }