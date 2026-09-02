from django import forms
from django.core.validators import RegexValidator

phone_validator = RegexValidator(r"^09\d{9}$", "شماره موبایل معتبر نیست (مثال: 09123456789)")


class CheckoutForm(forms.Form):
    """Every field here matches an input in checkout.html one-to-one —
    required/optional exactly matches whether that input has the HTML
    "required" attribute in the template.
    """

    # ---- Section 1: مشخصات تحویل‌گیرنده ----
    full_name = forms.CharField(label="نام و نام خانوادگی", max_length=150)
    phone = forms.CharField(label="شماره همراه", max_length=11, validators=[phone_validator])
    email = forms.EmailField(label="آدرس ایمیل", required=False)
    national_code = forms.CharField(label="کد ملی", max_length=10, required=False)

    # ---- Section 2: آدرس دقیق محل تحویل ----
    province = forms.CharField(label="استان", max_length=50)
    city = forms.CharField(label="شهر", max_length=50)
    full_address = forms.CharField(label="آدرس کامل پستی", widget=forms.Textarea(attrs={"rows": 2}))
    postal_code = forms.CharField(label="کد پستی", max_length=10)
    plaque = forms.CharField(label="پلاک", max_length=20)
    unit = forms.CharField(label="واحد", max_length=20, required=False)

    # ---- Section 4: روش پرداخت ----
    payment_method = forms.ChoiceField(
        label="روش پرداخت", choices=[("online", "پرداخت اینترنتی")], initial="online"
    )

    # ---- Sidebar: کد تخفیف ----
    coupon_code = forms.CharField(label="کد تخفیف", max_length=50, required=False)