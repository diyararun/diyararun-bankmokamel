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
