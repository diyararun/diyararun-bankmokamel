"""Digit-glyph conversion between ASCII (0-9) and Persian (۰-۹) numerals.

Used in two opposite directions across the project:

- Display (apps/store/templatetags/toman.py): ASCII -> Persian, so a
  price/amount prints the way a Persian-speaking shopper reads it.
- Admin input (apps/store/admin_persian_numbers.py): Persian (or
  Arabic-indic) -> ASCII, so a seller typing Persian digits into a
  number field in the Django admin doesn't hit a "این مقدار عدد صحیح
  نیست" validation error just because their keyboard is set to Persian.

Kept in one place so both directions agree on exactly which glyphs map
to which digit, instead of each call site maintaining its own table.
"""

_ASCII = "0123456789"
_PERSIAN = "۰۱۲۳۴۵۶۷۸۹"
# Arabic-indic digits (٠-٩) are a different set of glyphs than Persian
# (۰-۹) for the same values — a seller on an Arabic keyboard layout, or
# whose phone auto-switched digit shapes, could easily produce these
# instead. Normalizing both to ASCII costs nothing extra.
_ARABIC_INDIC = "٠١٢٣٤٥٦٧٨٩"

TO_PERSIAN = str.maketrans(_ASCII, _PERSIAN)
TO_ASCII = str.maketrans(_PERSIAN + _ARABIC_INDIC, _ASCII + _ASCII)


def to_persian_digits(value):
    """ASCII digits -> Persian digits. Non-digit characters (commas,
    minus signs, decimal points, other text) pass through untouched."""
    return str(value).translate(TO_PERSIAN)


def to_ascii_digits(value):
    """Persian or Arabic-indic digits -> ASCII digits. Non-digit
    characters pass through untouched."""
    return str(value).translate(TO_ASCII)
