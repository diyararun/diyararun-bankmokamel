import { postForm } from "../csrf.js";

// checkout.js: the order summary (cart items, prices) is rendered
// server-side by orders/checkout.html from the real Order/cart data, and
// the form submits natively (POST) to CheckoutView — no JS interception
// needed for that part.
//
// NOTE for whoever reads this next: this file used to contain an older,
// mock version (fake cart items, a fullName/phone/... getElementById
// block referencing ids that don't exist in the real Django-rendered
// form, and a handleFinalSubmit() that called event.preventDefault() and
// never actually submitted to the server). None of that ever got removed
// from the branch even after the real checkout flow was wired up — it
// was simply dead code that happened not to run (checkout.html no longer
// calls onsubmit="handleFinalSubmit(event)"), but importing this module
// would still throw at load time from the getElementById(...).addEventListener
// calls on null elements. Replaced outright rather than patched.
//
// Deferred on purpose, not silently dropped:
//   - Delivery-date calendar: Order has no delivery-date field at all
//     yet; add both together once that concept exists in the backend.

function initCouponForm() {
  const applyBtn = document.getElementById("couponApplyBtn");
  const input = document.getElementById("couponCodeInput");
  const messageEl = document.getElementById("couponMessage");
  const discountRow = document.getElementById("couponDiscountRow");
  const discountAmountEl = document.getElementById("couponDiscountAmount");
  const finalTotalEl = document.getElementById("finalTotalPrice");
  const breakdown = document.getElementById("priceBreakdown");
  if (!applyBtn || !input || !breakdown) return;

  const subtotal = Number(breakdown.dataset.subtotal);
  const shippingCost = Number(breakdown.dataset.shippingCost);

  function showMessage(text, isSuccess) {
    messageEl.textContent = text;
    messageEl.className = `text-[11px] mt-1.5 font-bold ${
      isSuccess ? "text-emerald-600" : "text-red-600"
    }`;
    messageEl.classList.remove("hidden");
  }

  applyBtn.addEventListener("click", async () => {
    const code = input.value.trim();
    if (!code) {
      showMessage("لطفاً یک کد تخفیف وارد کنید.", false);
      return;
    }

    applyBtn.disabled = true;
    let result;
    try {
      result = await postForm("/coupons/apply/", { code });
    } catch {
      applyBtn.disabled = false;
      showMessage("خطا در برقراری ارتباط. دوباره تلاش کنید.", false);
      return;
    }
    applyBtn.disabled = false;

    if (!result.valid) {
      discountRow.classList.add("hidden");
      finalTotalEl.innerText = `${subtotal + shippingCost} تومان`;
      showMessage(result.message, false);
      return;
    }

    discountAmountEl.innerText = `${result.discount_amount} تومان`;
    discountRow.classList.remove("hidden");
    finalTotalEl.innerText = `${subtotal - result.discount_amount + shippingCost} تومان`;
    showMessage(result.message, true);
  });
}

document.addEventListener("DOMContentLoaded", () => {
  initCouponForm();
});