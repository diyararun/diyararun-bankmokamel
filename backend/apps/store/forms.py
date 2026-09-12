from django import forms

from .models import ContactMessage

INPUT_CLASS = "w-full p-3 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-red-600 transition-all"
LTR_INPUT_CLASS = INPUT_CLASS + " text-left placeholder:text-right"


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "phone", "email", "subject", "message"]
        labels = {
            "name": "نام و نام خانوادگی",
            "phone": "شماره تماس",
            "email": "آدرس ایمیل",
            "subject": "موضوع پیام",
            "message": "متن پیام شما",
        }
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "مثال: رضا محمدی", "class": INPUT_CLASS}),
            "phone": forms.TextInput(
                attrs={"placeholder": "۰۹۱۲۳۴۵۶۷۸۹", "dir": "ltr", "class": LTR_INPUT_CLASS}
            ),
            "email": forms.EmailInput(
                attrs={"placeholder": "name@example.com", "dir": "ltr", "class": LTR_INPUT_CLASS}
            ),
            "subject": forms.Select(attrs={"class": INPUT_CLASS + " cursor-pointer"}),
            "message": forms.Textarea(
                attrs={"rows": 5, "placeholder": "جزئیات پیام خود را اینجا بنویسید...", "class": INPUT_CLASS}
            ),
        }