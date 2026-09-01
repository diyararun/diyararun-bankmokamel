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