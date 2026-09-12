from django import template

register = template.Library()

# Used to turn ASCII digits (what Python's int/str formatting always
# produces, regardless of LANGUAGE_CODE) into Persian ones for display.
# Django's own number formatting (USE_THOUSAND_SEPARATOR + the fa-ir
# locale) already groups digits into thousands, but it never changes the
# glyphs themselves — that's a separate, deliberate step we do here.
_PERSIAN_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")


@register.filter(name="toman")
def toman(value):
    """Formats a price/amount (in toman) the way a Persian-speaking
    shopper expects to read it: thousands separated by a comma and
    written in Persian numerals — ``1000000`` becomes ``۱,۰۰۰,۰۰۰``.

    Meant to be the one place this formatting logic lives, instead of
    every template re-deriving it. Apply it directly to the raw
    number — chain it *after* `default`, not before, so a missing value
    still gets its fallback text (e.g. `{{ variant.price|default:"—"|toman }}`):
    anything that isn't a plain integer (None, "", an em dash, an
    already-formatted string) is returned untouched rather than raising,
    so a chained `default` value always survives.
    """
    try:
        number = int(value)
    except (TypeError, ValueError):
        return value
    return f"{number:,}".translate(_PERSIAN_DIGITS)
