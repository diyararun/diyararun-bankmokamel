import re

from django import forms

from .models import User


PHONE_RE = re.compile(r"^09\d{9}$")


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
