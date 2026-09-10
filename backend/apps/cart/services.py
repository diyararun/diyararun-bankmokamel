from .models import Cart


def get_cart(request, create=False):
    """Finds the current visitor's cart — by logged-in user if
    authenticated, otherwise by session key.

    create=False (used by the context processor on every page load):
    never writes to the DB. An anonymous visitor with no session yet, or
    with a session but no cart, simply gets None back — this avoids
    creating an empty Cart row for every single page view.

    create=True (used by the cart-modifying views): get_or_create()s the
    cart, creating a session for the visitor first if they don't have one
    yet.
    """
    if request.user.is_authenticated:
        if create:
            cart, _ = Cart.objects.get_or_create(user=request.user)
            return cart
        return Cart.objects.filter(user=request.user).first()

    session_key = request.session.session_key
    if not session_key:
        if not create:
            return None
        request.session.create()
        session_key = request.session.session_key

    if create:
        cart, _ = Cart.objects.get_or_create(session_key=session_key, user=None)
        return cart
    return Cart.objects.filter(session_key=session_key, user__isnull=True).first()


def merge_guest_cart_into_user(session_key, user):
    """Folds a guest (session-based) cart into the now-logged-in user's
    cart. This is what the Cart model's docstring flagged as "a follow-up,
    not part of this pass" — and its absence was the actual cause of the
    checkout page showing an empty order summary for a real, full cart:
    a visitor adds items while anonymous (cart keyed by session_key), then
    logs in to reach checkout; django.contrib.auth.login() rotates the
    session key for security, so from that point on get_cart(request)
    looks up Cart.objects.filter(user=request.user) — a DIFFERENT, empty
    cart — while the actual items stay stranded on the old session_key.

    MUST be called with the session key captured *before* login() runs,
    since login() is what invalidates it.
    """
    if not session_key:
        return

    guest_cart = Cart.objects.filter(session_key=session_key, user__isnull=True).first()
    if guest_cart is None:
        return

    user_cart, _ = Cart.objects.get_or_create(user=user)
    for item in guest_cart.items.select_related("variant").all():
        existing = user_cart.items.filter(variant=item.variant).first()
        if existing:
            existing.quantity += item.quantity
        else:
            existing = item
            existing.pk = None
            existing.cart = user_cart
        # Same stock guard CartAddView uses — a guest's cart can predate a
        # stock change, and login is a legitimate moment to re-clamp it.
        if existing.quantity > item.variant.stock:
            existing.quantity = item.variant.stock
        existing.save()

    guest_cart.delete()


def serialize_cart(cart):
    """Turns a Cart into the plain dict the frontend JS renders the drawer
    from. Kept separate from the model so response shape changes don't
    touch models.py.
    """
    if cart is None:
        return {"items": [], "total_quantity": 0, "total_price": 0}

    items = []
    for item in cart.items.select_related("variant__product", "variant__flavor").all():
        variant = item.variant
        product = variant.product
        image = product.images.filter(is_primary=True).first() or product.images.first()
        items.append(
            {
                "item_id": item.id,
                "variant_id": variant.id,
                "product_name": product.name,
                "variant_label": variant.label,
                "flavor": variant.flavor.name if variant.flavor else None,
                "price": variant.price,
                # None when the variant has no discount — callers that sum
                # per-item savings must treat None as "no discount", not 0
                # confused with "compare price equals price".
                "compare_at_price": variant.compare_at_price,
                "quantity": item.quantity,
                "total_price": item.total_price,
                "image_url": image.image.url if image else None,
                "product_url": f"/products/{product.slug}/",
            }
        )

    return {
        "items": items,
        "total_quantity": sum(i["quantity"] for i in items),
        "total_price": sum(i["total_price"] for i in items),
    }


def product_discount_total(cart_data):
    """Sum of (compare_at_price - price) * quantity across a serialized
    cart's items — how much the customer is saving from per-product sale
    prices alone, separate from any coupon/campaign discount. Informational
    only: it does NOT get subtracted from total_price again, since
    variant.price (what total_price is built from) is already the
    discounted price the customer pays.
    """
    total = 0
    for item in cart_data["items"]:
        compare_at = item["compare_at_price"]
        if compare_at and compare_at > item["price"]:
            total += (compare_at - item["price"]) * item["quantity"]
    return total