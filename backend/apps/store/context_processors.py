from apps.cart.services import get_cart

from .models import SiteSettings


def cart(request):
    """Makes the cart badge count available on every page (server-rendered
    on first load), so the badge shows the real persisted count
    immediately instead of starting at 0 until cartDrawer.js runs.

    Uses create=False — a page view alone should never create an empty
    Cart row for a visitor who hasn't added anything yet.
    """
    current_cart = get_cart(request, create=False)
    total_quantity = current_cart.total_quantity if current_cart else 0
    return {"cart_total_quantity": total_quantity}


def site_settings(request):
    """Makes the editable site-wide content (hero copy, footer/contact
    info, social links, about-page text) available on every page as
    {{ site_settings.* }}, so header/footer partials and any page can use
    it without each view fetching it manually.
    """
    return {"site_settings": SiteSettings.load()}