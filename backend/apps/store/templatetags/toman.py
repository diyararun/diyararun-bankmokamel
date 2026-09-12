from django import template

from apps.store.persian_numerals import to_persian_digits

register = template.Library()


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
    return to_persian_digits(f"{number:,}")
