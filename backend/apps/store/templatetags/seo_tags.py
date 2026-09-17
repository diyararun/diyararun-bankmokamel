from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def absolute_url(context, relative_url):
    """Turns a MEDIA_URL-relative path (e.g. ``some_image_field.url``)
    into a fully-qualified absolute URL — نشست ۵۲.

    Open Graph / Twitter Card tags (``og:image``, ``twitter:image``)
    require an absolute URL; a relative one is silently ignored by
    Facebook/Telegram/Twitter's link-preview crawlers, which don't know
    our domain the way a browser rendering the page does.

    Needed because ``request.build_absolute_uri(path)`` can't be called
    directly from a template — dot-lookup in Django templates only
    supports no-argument method/property access, not passing an
    argument like ``path``.

    Returns "" for a falsy/missing url (instead of raising) so
    ``{% if some_field %}{% absolute_url some_field.url %}{% endif %}``
    keeps working the same way a plain ``{{ some_field.url }}`` would.
    """
    if not relative_url:
        return ""
    request = context.get("request")
    if request is None:
        return relative_url
    return request.build_absolute_uri(relative_url)
