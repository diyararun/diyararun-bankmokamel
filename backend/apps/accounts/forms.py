import re

from django import forms

from apps.store.validators import (
    validate_digits_only,
    validate_national_code,
    validate_persian_letters,
    validate_postal_code,
)

from .models import Address, User


PHONE_RE = re.compile(r"^09\d{9}$")

ADDRESS_INPUT_CLASS = (
    "w-full p-3 bg-slate-50 border border-slate-200 rounded-xl text-xs "
    "focus:outline-none focus:ring-2 focus:ring-red-600 transition-all"
)
ADDRESS_LTR_INPUT_CLASS = ADDRESS_INPUT_CLASS + " text-left placeholder:text-right"
ADDRESS_HALF_INPUT_CLASS = ADDRESS_INPUT_CLASS.replace("w-full ", "")


class PhoneForm(forms.Form):
    phone = forms.CharField(label="شماره همراه", max_length=11)

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        if not PHONE_RE.match(phone):
            raise forms.ValidationError("شماره موبایل معتبر نیست.")
        return phone


class OtpVerifyForm(forms.Form):
    phone = forms.CharField(max_length=11)
    code = forms.CharField(max_length=5)


class ProfileForm(forms.ModelForm):
    """فرم ویرایش اطلاعات کاربری - صفحه‌ی پروفایل استاندارد."""

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "national_code"]
        labels = {
            "first_name": "نام",
            "last_name": "نام خانوادگی",
            "email": "ایمیل",
            "national_code": "کد ملی",
        }
        INPUT_CLASS = (
            "w-full p-3.5 bg-slate-50 border border-slate-200 rounded-2xl text-sm "
            "font-bold focus:outline-none focus:ring-2 focus:ring-red-600 transition-all"
        )
        widgets = {
            "first_name": forms.TextInput(
                attrs={"placeholder": "مثلاً علی", "class": INPUT_CLASS}
            ),
            "last_name": forms.TextInput(
                attrs={"placeholder": "مثلاً محمدی", "class": INPUT_CLASS}
            ),
            "email": forms.EmailInput(
                attrs={"placeholder": "example@mail.com", "dir": "ltr", "class": INPUT_CLASS}
            ),
            "national_code": forms.TextInput(
                attrs={"placeholder": "۱۰ رقم", "dir": "ltr", "class": INPUT_CLASS}
            ),
        }

    def clean_national_code(self):
        # این فیلد قبلاً هیچ اعتبارسنجی‌ای نداشت — حالا از همان تابع
        # مشترکی استفاده می‌کند که فرم تسویه‌حساب و فرم آدرس‌های من هم
        # استفاده می‌کنند (apps.store.validators)، تا کد ملی وارد‌شده در
        # پروفایل هم واقعاً معتبر باشد.
        value = self.cleaned_data["national_code"].strip()
        validate_national_code(value)
        return value

    # نشست ۳۵: تا همین‌جا نام/نام‌خانوادگی هیچ قانونی نداشتند، با این‌که
    # apps.store.validators از همان اول (نگاه کنید به docstring بالای آن
    # فایل) دقیقاً برای اشتراک بین فرم تسویه‌حساب، فرم آدرس‌ها، *و* فرم
    # پروفایل نوشته شده بود. همان تابعی که full_name در آن دو فرم دیگر
    # استفاده می‌کند، اینجا هم روی هرکدام از این دو فیلد جدا اجرا می‌شود.
    def clean_first_name(self):
        value = self.cleaned_data["first_name"].strip()
        validate_persian_letters(value, "نام")
        return value

    def clean_last_name(self):
        value = self.cleaned_data["last_name"].strip()
        validate_persian_letters(value, "نام خانوادگی")
        return value


class AddressForm(forms.ModelForm):
    """فرم افزودن/ویرایش یک آدرس در «آدرس‌های من». همان فیلدها و همان
    قوانین اعتبارسنجی‌ای که فرم تسویه‌حساب دارد (apps.orders.forms.CheckoutForm)
    — چون این دقیقاً همان اطلاعاتی است که آن‌جا هم جمع می‌شود، فقط این‌بار
    قابل‌ذخیره برای دفعات بعد.
    """

    class Meta:
        model = Address
        fields = [
            "title",
            "full_name",
            "phone",
            "province",
            "city",
            "full_address",
            "postal_code",
            "plaque",
            "unit",
            "is_default",
        ]
        labels = {
            "title": "عنوان آدرس",
            "full_name": "نام و نام خانوادگی تحویل‌گیرنده",
            "phone": "شماره همراه",
            "province": "استان",
            "city": "شهر",
            "full_address": "آدرس کامل پستی",
            "postal_code": "کد پستی",
            "plaque": "پلاک",
            "unit": "واحد",
            "is_default": "این آدرس، آدرس پیش‌فرض من باشد",
        }
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "مثال: خانه، محل کار", "class": ADDRESS_INPUT_CLASS}),
            "full_name": forms.TextInput(
                attrs={"placeholder": "مثال: محمدجواد ابراهیمی", "class": ADDRESS_INPUT_CLASS}
            ),
            "phone": forms.TextInput(
                attrs={"placeholder": "۰۹۱۲۳۴۵۶۷۸۹", "dir": "ltr", "class": ADDRESS_LTR_INPUT_CLASS}
            ),
            "province": forms.TextInput(attrs={"placeholder": "تهران", "class": ADDRESS_INPUT_CLASS}),
            "city": forms.TextInput(attrs={"placeholder": "تهران", "class": ADDRESS_INPUT_CLASS}),
            "full_address": forms.Textarea(
                attrs={"rows": 2, "placeholder": "خیابان، کوچه، پلاک، واحد...", "class": ADDRESS_INPUT_CLASS}
            ),
            "postal_code": forms.TextInput(
                attrs={"placeholder": "۱۲۳۴۵۶۷۸۹۰", "maxlength": "10", "dir": "ltr", "class": ADDRESS_LTR_INPUT_CLASS}
            ),
            "plaque": forms.TextInput(attrs={"placeholder": "پلاک", "class": ADDRESS_HALF_INPUT_CLASS}),
            "unit": forms.TextInput(attrs={"placeholder": "واحد", "class": ADDRESS_HALF_INPUT_CLASS}),
        }

    def clean_phone(self):
        value = self.cleaned_data["phone"].strip()
        if not PHONE_RE.match(value):
            raise forms.ValidationError("شماره موبایل معتبر نیست (مثال: 09123456789)")
        return value

    def clean_full_name(self):
        value = self.cleaned_data["full_name"].strip()
        if len(value) < 3:
            raise forms.ValidationError("نام و نام خانوادگی باید حداقل ۳ کاراکتر باشد.")
        validate_persian_letters(value, "نام و نام خانوادگی")
        return value

    def clean_province(self):
        value = self.cleaned_data["province"].strip()
        validate_persian_letters(value, "نام استان")
        return value

    def clean_city(self):
        value = self.cleaned_data["city"].strip()
        validate_persian_letters(value, "نام شهر")
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
        validate_postal_code(value)
        return value

    def clean_plaque(self):
        value = self.cleaned_data["plaque"].strip()
        validate_digits_only(value, "شماره پلاک")
        return value

    def clean_unit(self):
        value = self.cleaned_data["unit"].strip()
        validate_digits_only(value, "شماره واحد")
        return value
