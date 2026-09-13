from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.generic import View

from apps.cart.services import get_cart, serialize_cart

from .services import validate_coupon


class ApplyCouponView(LoginRequiredMixin, View):
    """POST /coupons/apply/ — body: code.

    Only a preview: validates the code against the customer's real,
    current cart and reports back the discount, but doesn't reserve
    anything or create a CouponRedemption. Login-gated for the same
    reason checkout itself is — a coupon's one-per-user rule is
    meaningless for a request with no real user attached, and there is
    nothing to apply a coupon to before reaching checkout anyway.
    """

    # By the time this endpoint is reachable in the UI, the customer is
    # already logged in (it only appears on the checkout page, which
    # itself requires login) — but a session can still expire mid-page,
    # so this guards against a redirect-to-login HTML page landing in a
    # fetch() call expecting JSON.
    def handle_no_permission(self):
        return JsonResponse(
            {"valid": False, "message": "برای اعمال کد تخفیف باید وارد حساب کاربری خود شوید."},
            status=401,
        )

    def post(self, request):
        code = request.POST.get("code", "")
        cart = get_cart(request, create=False)
        cart_data = serialize_cart(cart)
        subtotal = cart_data["total_price"]

        coupon, discount_amount, error = validate_coupon(code, request.user, subtotal)
        if error:
            return JsonResponse({"valid": False, "message": error}, status=400)

        return JsonResponse(
            {
                "valid": True,
                "code": coupon.code,
                "discount_amount": discount_amount,
                "message": "کد تخفیف با موفقیت اعمال شد.",
            }
        )