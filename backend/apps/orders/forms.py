from django import forms
from django.core.validators import RegexValidator

phone_validator = RegexValidator(r"^09\d{9}$", "شماره موبایل معتبر نیست (مثال: 09123456789)")

# Same class-naming convention as apps/store/forms.py, so widget markup
# rendered by {{ form.field }} keeps checkout.html's original look exactly.
INPUT_CLASS = (
    "w-full p-3 bg-slate-50 border border-slate-200 rounded-xl text-xs "
    "focus:outline-none focus:ring-2 focus:ring-red-600 transition-all"
)
LTR_INPUT_CLASS = INPUT_CLASS + " text-left placeholder:text-right"
HALF_INPUT_CLASS = INPUT_CLASS.replace("w-full ", "")  # for the plaque/unit side-by-side pair


class CheckoutForm(forms.Form):
    """Every field here matches an input in checkout.html one-to-one —
    required/optional exactly matches whether that input has the HTML
    "required" attribute in the template.
    """

    # ---- Section 1: مشخصات تحویل‌گیرنده ----
    full_name = forms.CharField(
        label="نام و نام خانوادگی",
        max_length=150,
        widget=forms.TextInput(attrs={"placeholder": "مثال: محمدجواد ابراهیمی", "class": INPUT_CLASS}),
    )
    phone = forms.CharField(
        label="شماره همراه",
        max_length=11,
        validators=[phone_validator],
        widget=forms.TextInput(
            attrs={"placeholder": "۰۹۱۲۳۴۵۶۷۸۹", "pattern": "09[0-9]{9}", "dir": "ltr", "class": LTR_INPUT_CLASS}
        ),
    )
    email = forms.EmailField(
        label="آدرس ایمیل",
        required=False,
        widget=forms.EmailInput(attrs={"placeholder": "name@example.com", "dir": "ltr", "class": LTR_INPUT_CLASS}),
    )
    national_code = forms.CharField(
        label="کد ملی",
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "۰۰۱۲۳۴۵۶۷۸", "dir": "ltr", "class": LTR_INPUT_CLASS}),
    )

    # ---- Section 2: آدرس دقیق محل تحویل ----
    province = forms.CharField(
        label="استان", max_length=50, widget=forms.TextInput(attrs={"placeholder": "تهران", "class": INPUT_CLASS})
    )
    city = forms.CharField(
        label="شهر", max_length=50, widget=forms.TextInput(attrs={"placeholder": "تهران", "class": INPUT_CLASS})
    )
    full_address = forms.CharField(
        label="آدرس کامل پستی",
        widget=forms.Textarea(
            attrs={"rows": 2, "placeholder": "خیابان، کوچه، پلاک، واحد...", "class": INPUT_CLASS}
        ),
    )
    postal_code = forms.CharField(
        label="کد پستی",
        max_length=10,
        widget=forms.TextInput(
            attrs={"placeholder": "۱۲۳۴۵۶۷۸۹۰", "maxlength": "10", "dir": "ltr", "class": LTR_INPUT_CLASS}
        ),
    )
    plaque = forms.CharField(
        label="پلاک",
        max_length=20,
        widget=forms.TextInput(attrs={"placeholder": "پلاک", "class": HALF_INPUT_CLASS}),
    )
    unit = forms.CharField(
        label="واحد",
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "واحد", "class": HALF_INPUT_CLASS}),
    )

    # ---- Section 4: روش پرداخت ----
    # Only one option exists today, so a visible radio/select isn't useful
    # to the customer — the choice is rendered manually as a static card in
    # checkout.html and this field just carries the value along as hidden
    # input. Kept as a ChoiceField (not hardcoded) so Order.objects.create()
    # still gets it through the normal validated cleaned_data path.
    payment_method = forms.ChoiceField(
        label="روش پرداخت",
        choices=[("online", "پرداخت اینترنتی")],
        initial="online",
        widget=forms.HiddenInput(),
    )

    # ---- Sidebar: کد تخفیف ----
    # Not wired to real validation yet — deferred on purpose to the future
    # "coupons" app (see decision in orders/models.py). The input is
    # rendered disabled in checkout.html, so it always submits empty and
    # discount_amount stays 0 in the view.
    coupon_code = forms.CharField(
        label="کد تخفیف",
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "به‌زودی...", "disabled": True, "class": ""}),
    )