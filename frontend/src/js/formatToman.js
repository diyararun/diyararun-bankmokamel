// Client-side mirror of the `toman` Django template filter
// (apps/store/templatetags/toman.py) — keep the two in sync if the
// display format ever changes.
//
// This exists because prices painted by the server (product page loads,
// list pages) and prices repainted in the browser after an interaction
// (switching a variant, opening the cart drawer, typing into the header
// search box) have to look identical, not just "close enough" —
// Number.prototype.toLocaleString("fa-IR") gets close but uses "٬" (the
// Arabic thousands separator) instead of a plain comma, which doesn't
// match the format used everywhere else on the site.
const PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹";

// نشست ۴۴: قبلاً این تبدیل فقط این‌جا، داخل formatToman، وجود داشت.
// شمارش‌معکوسِ رزروِ موجودی (entries/orderDetail.js) هم دقیقاً به همین
// «رقمِ لاتین → رقمِ فارسی» نیاز داشت، برای همین به یک تابعِ جدا استخراج
// شد تا دوباره‌نویسیِ همان جدولِ PERSIAN_DIGITS در یک فایلِ دیگر لازم
// نباشد.
export function toPersianDigits(value) {
  return String(value).replace(/\d/g, (digit) => PERSIAN_DIGITS[digit]);
}

export function formatToman(value) {
  const number = Math.trunc(Number(value));
  if (!Number.isFinite(number)) return String(value);
  return toPersianDigits(number.toLocaleString("en-US"));
}
