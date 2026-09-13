import re

from django import forms
from django.core.validators import RegexValidator

phone_validator = RegexValidator(r"^09\d{9}$", "شماره موبایل معتبر نیست (مثال: 09123456789)")

# ‌ = نیم‌فاصله (ZWNJ) — بدونش نوشتن کلماتی مثل «می‌خواهم» با فاصله‌ی
# معمولی رد می‌شود که برای فیلد نام/شهر/استان اذیت‌کننده است. خط تیره هم
# مجاز است (مثل نام‌های ترکیبی)، دقیقاً همان کاراکترهایی که نسخه‌ی قبلی
# (و ناقص) اعتبارسنجی سمت فرانت‌اند در checkout.js مجاز می‌شمرد.
PERSIAN_LETTERS_RE = re.compile(r"^[آ-ی\s‌-]+$")


def _is_valid_iranian_national_code(code):
    """همان الگوریتم چک‌سام استاندارد کد ملی ایران که سمت فرانت‌اند
    (checkout.js، تابع isValidIranianNationalCode) هم پیاده‌سازی شده —
    اینجا دوباره (و این‌بار واقعاً) روی سرور اجرا می‌شود، چون اعتبارسنجی
    جاوااسکریپت به‌تنهایی هیچ تضمینی نمی‌دهد (کاربر می‌تواند جاوااسکریپت را
    غیرفعال کند یا مستقیم POST بزند).
    """
    if not re.fullmatch(r"\d{10}", code):
        return False
    if code == code[0] * 10:
        return False
    check = int(code[9])
    total = sum(int(code[i]) * (10 - i) for i in range(9))
    remainder = total % 11
    digit = remainder if remainder < 2 else 11 - remainder
    return digit == check

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
    # Real, server-validated coupon codes now (apps.coupons) — see
    # orders/views.py::CheckoutView for where this is actually checked.
    # dir="ltr" + uppercase because coupon codes are conventionally typed
    # in Latin letters; Coupon.save() also normalizes to uppercase, so a
    # customer typing lowercase still matches.
    coupon_code = forms.CharField(
        label="کد تخفیف",
        max_length=50,
        required=False,
        widget=forms.TextInput(
            attrs={
                "id": "couponCodeInput",
                "placeholder": "کد تخفیف را وارد کنید",
                "dir": "ltr",
                "class": INPUT_CLASS.replace("w-full ", "flex-1 ") + " uppercase placeholder:normal-case",
            }
        ),
    )

    # ------------------------------------------------------------------
    # این clean_<field>ها دقیقاً همان قاعده‌هایی هستند که checkout.js از قبل
    # سمت فرانت‌اند (به‌صورت ناقص/شکسته) پیاده‌سازی کرده بود — این‌جا برای
    # اولین‌بار واقعاً روی سرور هم اجرا می‌شوند. جزئیات «چرا هر دو لایه لازم
    # است» را در توضیح این نشست، جدا از کد، بیان می‌کنم.
    # ------------------------------------------------------------------

    def clean_full_name(self):
        value = self.cleaned_data["full_name"].strip()
        if len(value) < 3:
            raise forms.ValidationError("نام و نام خانوادگی باید حداقل ۳ کاراکتر باشد.")
        if not PERSIAN_LETTERS_RE.match(value):
            raise forms.ValidationError("نام و نام خانوادگی باید فقط شامل حروف فارسی باشد.")
        return value

    def clean_province(self):
        value = self.cleaned_data["province"].strip()
        if not PERSIAN_LETTERS_RE.match(value):
            raise forms.ValidationError("نام استان باید فقط شامل حروف فارسی باشد.")
        return value

    def clean_city(self):
        value = self.cleaned_data["city"].strip()
        if not PERSIAN_LETTERS_RE.match(value):
            raise forms.ValidationError("نام شهر باید فقط شامل حروف فارسی باشد.")
        return value

    def clean_full_address(self):
        value = self.cleaned_data["full_address"].strip()
        if len(value) < 10:
            raise forms.ValidationError("آدرس وارد شده خیلی کوتاه است.")
        if len(value) > 500:
            raise forms.ValidationError("آدرس نمی‌تواند بیشتر از ۵۰۰ کاراکتر باشد.")
        return value

    def clean_postal_code(self):
        value = self.cleaned_data["postal_code"].strip()
        if not re.fullmatch(r"\d{10}", value):
            raise forms.ValidationError("کد پستی باید دقیقاً ۱۰ رقم باشد.")
        return value

    def clean_plaque(self):
        value = self.cleaned_data["plaque"].strip()
        if not re.fullmatch(r"\d+", value):
            raise forms.ValidationError("شماره پلاک معتبر نیست.")
        return value

    def clean_unit(self):
        value = self.cleaned_data["unit"].strip()
        # اختیاری است — فقط وقتی چیزی وارد شده باشد بررسی می‌کنیم.
        if value and not re.fullmatch(r"\d+", value):
            raise forms.ValidationError("شماره واحد معتبر نیست.")
        return value

    def clean_national_code(self):
        value = self.cleaned_data["national_code"].strip()
        # اختیاری است (برای صدور فاکتور رسمی) — اگر خالی گذاشته شود مشکلی
        # نیست، اما اگر چیزی وارد شود باید واقعاً یک کد ملی معتبر باشد.
        if value and not _is_valid_iranian_national_code(value):
            raise forms.ValidationError("کد ملی معتبر نیست.")
        return value