import { postForm } from "../csrf.js";
import { formatToman } from "../formatToman.js";

// ======================== اعتبارسنجی سمت کلاینت فرم پرداخت =========================
//
// این فایل قبلاً یک نسخه‌ی قدیمی و mock داشت: به آی‌دی‌های غیرواقعی مثل
// fullName/phone/... ارجاع می‌داد که در HTML واقعی این صفحه اصلاً وجود
// نداشتند، یک آکولاد باز بدون بسته داشت (خطای syntax واقعی — با
// `node --check` قابل تکرار است)، یک سبد خرید ساختگی رندر می‌کرد، و
// handleFinalSubmit() اصلاً به سرور POST نمی‌کرد. همه‌ی این‌ها به‌خاطر یک
// conflict قدیمی هنگام pull باقی مانده بود و هیچ‌کدام واقعاً روی فرم اعمال
// نمی‌شد. این فایل کامل بازنویسی شده است.
//
// نکته‌ی مهم: اعتبارسنجی این‌جا («فقط حرف فارسی»، «فقط رقم») صرفاً برای
// تجربه‌ی کاربری (UX) است — جلوگیری از تایپ یک کاراکتر اشتباه، نه یک لایه‌ی
// امنیتی. تنها منبع مورد اعتماد برای صحت داده همان clean_<field>های سمت
// بک‌اند در apps/orders/forms.py هستند: کاربری که جاوااسکریپت را غیرفعال
// کند، یا مستقیماً به CheckoutView پست بزند، همچنان توسط بک‌اند بررسی
// می‌شود. فرم سمت سرور هم دوباره (و به‌طور کامل) همین قوانین را بررسی
// می‌کند تا هرگز به داده‌ی سمت کلاینت اعتماد نشود.

const NAV_KEYS = [
  "Backspace",
  "Delete",
  "ArrowLeft",
  "ArrowRight",
  "Tab",
  "Home",
  "End",
];

const PERSIAN_LETTER_KEY_RE = /^[آ-ی\s‌-]$/;

function onlyPersianLettersKeydown(event) {
  if (
    !PERSIAN_LETTER_KEY_RE.test(event.key) &&
    !NAV_KEYS.includes(event.key) &&
    !(event.ctrlKey || event.metaKey)
  ) {
    event.preventDefault();
  }
}

function sanitizePersianInput(event) {
  event.target.value = event.target.value.replace(/[^آ-ی\s‌-]/g, "");
}

function onlyDigitsKeydown(event) {
  if (
    !/^[0-9]$/.test(event.key) &&
    !NAV_KEYS.includes(event.key) &&
    !(event.ctrlKey || event.metaKey)
  ) {
    event.preventDefault();
  }
}

function sanitizeDigitsInput(event) {
  event.target.value = event.target.value.replace(/\D/g, "");
}

function bindField(id, onKeydown, onInput) {
  const el = document.getElementById(id);
  if (!el) return;
  el.addEventListener("keydown", onKeydown);
  el.addEventListener("input", onInput);
}

// آی‌دی‌های واقعی، همان‌طور که Django برای هر فیلد CheckoutForm می‌سازد
// (id_<نام فیلد> — پیش‌فرض ویجت‌های جنگو، به‌جز coupon_code که در forms.py
// صراحتاً id="couponCodeInput" گرفته و initCouponForm جدا مدیریتش می‌کند).
function initFieldValidation() {
  ["id_full_name", "id_province", "id_city"].forEach((id) =>
    bindField(id, onlyPersianLettersKeydown, sanitizePersianInput),
  );
  ["id_phone", "id_national_code", "id_postal_code", "id_plaque", "id_unit"].forEach(
    (id) => bindField(id, onlyDigitsKeydown, sanitizeDigitsInput),
  );
}

// ======================== کد تخفیف ========================
//
// قبلاً applyCoupon() یک تابع کاملاً ساختگی بود (فقط یک toast با «۱۰٪
// تخفیف» ثابت نشان می‌داد، بدون تماس واقعی با سرور) و اصلاً به دکمه‌ی
// واقعی #couponApplyBtn هم وصل نبود. حالا با apps.coupons.views.ApplyCouponView
// (همان endpoint واقعی /coupons/apply/ که سمت بک‌اند کد را با
// apps.coupons.services.validate_coupon اعتبارسنجی می‌کند) صحبت می‌کند.
function initCouponForm() {
  const applyBtn = document.getElementById("couponApplyBtn");
  const input = document.getElementById("couponCodeInput");
  const messageEl = document.getElementById("couponMessage");
  const discountRow = document.getElementById("couponDiscountRow");
  const discountAmountEl = document.getElementById("couponDiscountAmount");
  const finalTotalEl = document.getElementById("finalTotalPrice");
  const breakdown = document.getElementById("priceBreakdown");
  if (!applyBtn || !input || !breakdown) return;

  // این دو مقدار عمداً به‌صورت عدد خام (بدون فرمت) روی priceBreakdown
  // نشسته‌اند (نگاه کنید به checkout.html) — دقیقاً برای همین محاسبه.
  const subtotal = Number(breakdown.dataset.subtotal || 0);
  const shippingCost = Number(breakdown.dataset.shippingCost || 0);

  function showMessage(text, isError) {
    if (!messageEl) return;
    messageEl.textContent = text;
    messageEl.classList.remove("hidden");
    messageEl.classList.toggle("text-red-600", isError);
    messageEl.classList.toggle("text-emerald-600", !isError);
  }

  applyBtn.addEventListener("click", async () => {
    const code = input.value.trim();
    if (!code) {
      showMessage("لطفاً کد تخفیف را وارد کنید.", true);
      return;
    }

    applyBtn.disabled = true;
    try {
      const data = await postForm("/coupons/apply/", { code });

      if (!data.valid) {
        showMessage(data.message || "کد تخفیف نامعتبر است.", true);
        return;
      }

      showMessage(data.message, false);
      if (discountRow && discountAmountEl && finalTotalEl) {
        discountRow.classList.remove("hidden");
        discountAmountEl.textContent = `${formatToman(data.discount_amount)} تومان`;
        finalTotalEl.textContent = `${formatToman(
          subtotal - data.discount_amount + shippingCost,
        )} تومان`;
      }
    } catch (err) {
      showMessage("خطا در برقراری ارتباط. دوباره تلاش کنید.", true);
    } finally {
      applyBtn.disabled = false;
    }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  initFieldValidation();
  initCouponForm();
});
