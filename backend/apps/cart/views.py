from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import View

from apps.catalog.models import ProductVariant

from .services import get_cart, serialize_cart


class CartDetailView(View):
    """GET /cart/ — current cart state. Called on page load so the drawer
    and badge reflect the real (persisted) cart instead of resetting to
    empty on every navigation, which is the exact problem the frontend
    dev's own comment in cartDrawer.js flagged.
    """

    def get(self, request):
        cart = get_cart(request, create=False)
        return JsonResponse(serialize_cart(cart))


class CartAddView(View):
    """POST /cart/add/ — body: variant_id, quantity (default 1).
    Adds a new line or increments an existing one for that exact variant.
    """

    def post(self, request):
        variant_id = request.POST.get("variant_id")
        try:
            quantity = int(request.POST.get("quantity", 1))
        except (TypeError, ValueError):
            quantity = 1
        if quantity < 1:
            quantity = 1

        variant = get_object_or_404(ProductVariant, pk=variant_id, is_active=True)
        cart = get_cart(request, create=True)

        item, created = cart.items.get_or_create(variant=variant, defaults={"quantity": quantity})
        if not created:
            item.quantity += quantity

        # Don't let the cart quantity exceed real stock. This is a soft
        # guard for a nicer UX, not the final word — full stock
        # enforcement belongs at checkout time (orders app, next phase),
        # since stock can change between adding to cart and paying.
        if item.quantity > variant.stock:
            item.quantity = variant.stock
        item.save()

        return JsonResponse(serialize_cart(cart))


class CartUpdateView(View):
    """
    POST /cart/update/ — body: variant_id, delta (+1 / -1).
    Matches cartDrawer.js's updateQuantity(name, delta) behavior exactly:
    quantity <= 0 after the delta removes the line entirely.
    """

    def post(self, request):
        variant_id = request.POST.get("variant_id")
        try:
            delta = int(request.POST.get("delta", 0))
        except (TypeError, ValueError):
            delta = 0

        cart = get_cart(request, create=True)
        item = cart.items.filter(variant_id=variant_id).first()
        if item is not None:
            item.quantity += delta
            if item.quantity <= 0:
                item.delete()
            else:
                if item.quantity > item.variant.stock:
                    item.quantity = item.variant.stock
                item.save()

        return JsonResponse(serialize_cart(cart))


class CartRemoveView(View):
    """
    POST /cart/remove/ — body: variant_id. Removes a line outright
    (for a dedicated "remove" button, distinct from decrementing to 0).
    """

    def post(self, request):
        variant_id = request.POST.get("variant_id")
        cart = get_cart(request, create=True)
        cart.items.filter(variant_id=variant_id).delete()
        return JsonResponse(serialize_cart(cart))