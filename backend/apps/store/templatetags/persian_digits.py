from django import template

from apps.store.persian_numerals import to_persian_digits

register = template.Library()


@register.filter(name="persian_digits")
def persian_digits(value):
    """Converts any ASCII digits in `value` to Persian digits, leaving
    everything else (decimal points, parentheses, non-digit text)
    untouched — e.g. ``2.0`` -> ``۲.۰``, ``1`` -> ``۱``.

    Unlike `toman` (apps/store/templatetags/toman.py), this does NOT add
    thousands separators or require the value to be an integer — it's
    for things like a star rating average or a review count, not a
    price. Apply it after any other formatting filter (e.g.
    ``{{ product.average_rating|floatformat:1|default:"—"|persian_digits }}``),
    same convention as `toman`, so a missing value's fallback text
    survives untouched (to_persian_digits() only ever touches digit
    characters, so passing it something like "—" is already harmless,
    but chaining in this order keeps the convention consistent and
    obvious to read).
    """
    return to_persian_digits(value)
