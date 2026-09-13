"""Importing this module (for its side effect — see admin.py in catalog,
store, coupons, orders and reviews) patches Django admin's
FORMFIELD_FOR_DBFIELD_DEFAULTS so every plain integer/decimal field, in
ANY ModelAdmin, renders with PersianDigitNumberWidget instead of the
default number widget.

Why: Django's IntegerField normally renders as <input type="number">,
and most browsers enforce the HTML5 "valid floating-point number"
grammar on every keystroke — Persian digits (۰-۹) simply never reach
the field's value at all, the browser blocks them before they're typed.
So a seller whose keyboard is set to Persian (natural, on a Persian-
language admin) can't type a price, weight, or stock count without
switching to a Latin keyboard first, which is exactly the friction this
fixes. PersianDigitNumberWidget below is a plain text input instead
(no browser-side digit filtering) that silently normalizes Persian or
Arabic-indic digits to ASCII once the form is submitted, before
Django's own IntegerField.to_python() ever sees the value.

Mirrors the exact same "import a module for its patching side effect"
pattern already used for django_jalali.admin in this project (see the
comment atop apps/catalog/admin.py) — same idea, applied to plain
numbers instead of Jalali dates.

This module also exports PersianDigitCharAdminMixin, a small opt-in
mixin (NOT a global patch like the number-field one above) for the
handful of CharFields that are "numeric-looking" text — phone,
postal_code, national_code. Those are plain CharFields with no
built-in digit-only widget, so the FORMFIELD_FOR_DBFIELD_DEFAULTS trick
above doesn't touch them at all; unlike the pure number fields, a
Persian digit typed into one of these is happily accepted and saved
as-is (no browser-side blocking, no admin/db error) — it just silently
stores the wrong glyphs. For `phone` specifically this is a real bug,
not just a cosmetic one: the OTP-login regex (accounts/forms.py's
PHONE_RE = r"^09\d{9}$") has a literal ASCII "09" prefix that never
matches a Persian "۰۹" prefix, so a phone number edited via Persian
keyboard in admin silently locks that customer out of OTP login with
no error shown anywhere. See PersianDigitCharAdminMixin below for how
this is applied per-ModelAdmin.
"""

from django import forms
from django.contrib.admin.options import FORMFIELD_FOR_DBFIELD_DEFAULTS
from django.db import models as db_models

from .persian_numerals import to_ascii_digits


class PersianDigitNumberWidget(forms.TextInput):
    """A plain text box (not <input type="number">) that accepts
    Persian or Arabic-indic digits and converts them to ASCII on
    submit. `inputmode="decimal"` still gives touch devices a numeric
    keyboard — that's just an on-screen keyboard hint, unlike
    type="number" it doesn't restrict which characters can land in the
    field, so it doesn't reintroduce the problem this widget exists to
    avoid.
    """

    def __init__(self, attrs=None):
        merged_attrs = {"inputmode": "decimal"}
        if attrs:
            merged_attrs.update(attrs)
        super().__init__(merged_attrs)

    def value_from_datadict(self, data, files, name):
        value = super().value_from_datadict(data, files, name)
        if isinstance(value, str):
            return to_ascii_digits(value)
        return value


_NUMBER_FIELD_CLASSES = (
    db_models.IntegerField,
    db_models.SmallIntegerField,
    db_models.BigIntegerField,
    db_models.PositiveIntegerField,
    db_models.PositiveSmallIntegerField,
    db_models.PositiveBigIntegerField,
    db_models.DecimalField,
    db_models.FloatField,
)

for _field_cls in _NUMBER_FIELD_CLASSES:
    FORMFIELD_FOR_DBFIELD_DEFAULTS[_field_cls] = {"widget": PersianDigitNumberWidget}


class PersianDigitCharWidget(forms.TextInput):
    """Same Persian/Arabic-indic -> ASCII normalization as
    PersianDigitNumberWidget above, but for a plain CharField that's
    already a normal <input type="text"> — no `inputmode`/type override
    needed here, since text inputs never blocked Persian digits from
    being typed in the first place; the only problem is what gets
    *saved*, which value_from_datadict fixes the same way.
    """

    def value_from_datadict(self, data, files, name):
        value = super().value_from_datadict(data, files, name)
        if isinstance(value, str):
            return to_ascii_digits(value)
        return value


# Deliberately narrow: only CharFields whose value is really a run of
# digits (a phone number, a postal code, a national ID number) belong
# here. Free-text address fields (full_address, plaque, unit, a
# coupon's `code`, ...) are intentionally left alone — plaque/unit
# already validate digits-only at the *form* level (apps.store.validators
# .validate_digits_only, used by CheckoutForm/AddressForm), but that
# customer-facing form is separate from this admin-only widget, and
# those two fields aren't in the "breaks a real feature if wrong" tier
# that phone is.
PERSIAN_DIGIT_CHAR_FIELDS = {"phone", "postal_code", "national_code"}


class PersianDigitCharAdminMixin:
    """Mix into a ModelAdmin to normalize Persian/Arabic-indic digits on
    every field named in PERSIAN_DIGIT_CHAR_FIELDS (whichever of them
    the model actually has — a model missing one of the names simply
    never triggers this branch for it).

    This can't be a global FORMFIELD_FOR_DBFIELD_DEFAULTS patch like the
    number-field fix above, because that dict is keyed by *field class*
    (every CharField in the whole project, including free-text ones,
    shares one class) — there's no way to single out just these three
    field *names* without going through formfield_for_dbfield(), which
    is exactly what this mixin does.
    """

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name in PERSIAN_DIGIT_CHAR_FIELDS:
            kwargs["widget"] = PersianDigitCharWidget(attrs={"dir": "ltr"})
        return super().formfield_for_dbfield(db_field, request, **kwargs)
