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

from django.utils.safestring import mark_safe

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


# Default format for format_jalali_datetime(): full Jalali date + time,
# down to the second — no microseconds, no UTC offset. Both jdatetime's
# own datetime objects (what django-jalali's jDateTimeField returns) and
# plain Python datetimes understand these strftime directives, so this
# one function works whichever kind of value it's handed.
JALALI_DATETIME_FORMAT = "%Y/%m/%d - %H:%M:%S"


def format_jalali_datetime(value, fmt=JALALI_DATETIME_FORMAT):
    """Formats a django-jalali datetime (or a plain aware/naive datetime)
    into a clean, Persian-digit string — e.g. "۱۴۰۵/۰۶/۲۲ - ۱۰:۳۱:۴۰"
    instead of the raw "1405-06-22 10:31:40.878179+0330" that printing a
    jDateTimeField value directly (with no formatting at all) produces.

    Shared between the `jdatetime` template filter (apps/store/templatetags)
    and every admin.py that shows a date column, so the storefront and the
    admin panel format dates identically instead of each guessing at their
    own %-format string.
    """
    if not value:
        return value
    try:
        formatted = value.strftime(fmt)
    except (AttributeError, ValueError, TypeError):
        # Not a date/datetime-like value at all — return it unchanged
        # rather than raising, so a bad input never crashes a page/admin
        # list over what's ultimately just a display nicety.
        return value
    persian = to_persian_digits(formatted)
    # Wrapped in <bdi dir="ltr"> so the browser treats "YYYY/MM/DD - HH:MM:SS"
    # as one isolated left-to-right run, immune to the surrounding RTL
    # paragraph it's dropped into. Without this, this exact string (two
    # numeric groups joined by " - ", no strong RTL character anywhere
    # in it) gets visually reordered by the page's RTL bidi context —
    # which is exactly why the time was rendering before the date
    # instead of after: the same reason phone/postal-code/national-code
    # fields elsewhere in this project always get dir="ltr" on their
    # container, just applied here once, centrally, instead of at every
    # template/admin call site (and easy to forget at a new one).
    # mark_safe is fine here: the only content inside the tag is digits,
    # "/", " - ", and ":" — never anything from user input.
    return mark_safe(f'<bdi dir="ltr">{persian}</bdi>')
