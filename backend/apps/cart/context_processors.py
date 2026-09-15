from apps.cart.services import get_cart


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