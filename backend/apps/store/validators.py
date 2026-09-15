"""Shared field-level validators for anything that collects a person's
name, address, or national code — checkout (apps.orders.forms), saved
addresses (apps.accounts.forms), and the profile-edit form all need the
exact same rules ("فقط حروف فارسی" for a name/city, a real national-code
checksum, ...). This used to be written once inside apps.orders.forms and
would have been copy-pasted a second and third time for the addresses
feature — centralizing it here means one rule, one place to fix it.
"""

import re

from django import forms

# ‌ = نیم‌فاصله (ZWNJ) — بدونش نوشتن کلماتی مثل «می‌خواهم» با فاصله‌ی
# معمولی رد می‌شود. خط تیره هم مجاز است (نام‌های ترکیبی).
PERSIAN_LETTERS_RE = re.compile(r"^[آ-ی\s‌-]+$")

POSTAL_CODE_RE = re.compile(r"\d{10}")
DIGITS_ONLY_RE = re.compile(r"\d+")


def validate_persian_letters(value, field_label):
    """برای نام/استان/شهر: raise می‌کند اگر value چیزی غیر از حروف فارسی
    (و فاصله/نیم‌فاصله/خط‌تیره) داشته باشد."""
    if not PERSIAN_LETTERS_RE.fullmatch(value):
        raise forms.ValidationError(f"{field_label} باید فقط شامل حروف فارسی باشد.")


def validate_digits_only(value, field_label):
    """برای پلاک/واحد: اگر value خالی نباشد، باید فقط رقم باشد."""
    if value and not DIGITS_ONLY_RE.fullmatch(value):
        raise forms.ValidationError(f"{field_label} معتبر نیست.")


def validate_postal_code(value):
    if not POSTAL_CODE_RE.fullmatch(value):
        raise forms.ValidationError("کد پستی باید دقیقاً ۱۰ رقم باشد.")


def is_valid_iranian_national_code(code):
    """الگوریتم استاندارد چک‌سام کد ملی ایران: رقم دهم از روی ۹ رقم اول
    محاسبه می‌شود، پس هر رشته‌ی ۱۰ رقمی دلخواه یک کد ملی معتبر نیست."""
    if not re.fullmatch(r"\d{10}", code):
        return False
    if code == code[0] * 10:
        return False
    check = int(code[9])
    total = sum(int(code[i]) * (10 - i) for i in range(9))
    remainder = total % 11
    digit = remainder if remainder < 2 else 11 - remainder
    return digit == check


def validate_national_code(value):
    """کد ملی همیشه اختیاری است (برای صدور فاکتور رسمی) — فقط وقتی چیزی
    وارد شده، باید واقعاً معتبر باشد."""
    if value and not is_valid_iranian_national_code(value):
        raise forms.ValidationError("کد ملی معتبر نیست.")
