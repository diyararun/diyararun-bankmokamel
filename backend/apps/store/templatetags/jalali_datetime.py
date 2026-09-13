from django import template

from apps.store.persian_numerals import format_jalali_datetime

register = template.Library()


@register.filter(name="jdatetime")
def jdatetime(value):
    """Formats a django-jalali datetime value for display: ``{{
    order.created_at }}`` used to print the raw internal representation
    (microseconds and a UTC offset included — e.g.
    "1405-06-22 10:31:40.878179+0330"), because nothing ever told Django
    how to render it. ``{{ order.created_at|jdatetime }}`` prints
    "۱۴۰۵/۰۶/۲۲ - ۱۰:۳۱:۴۰" instead — same underlying moment, just a
    format an actual customer/admin is meant to read.
    """
    return format_jalali_datetime(value)
