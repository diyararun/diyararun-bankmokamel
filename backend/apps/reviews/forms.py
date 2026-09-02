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
    """

    rating = forms.ChoiceField(choices=RATING_CHOICES, label="امتیاز", widget=forms.RadioSelect)

    class Meta:
        model = Review
        fields = ["rating", "comment"]
        labels = {"comment": "متن دیدگاه"}
        widgets = {
            "comment": forms.Textarea(
                attrs={"rows": 4, "placeholder": "تجربه استفاده خود از این محصول را بنویسید..."}
            ),
        }