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

export function formatToman(value) {
  const number = Math.trunc(Number(value));
  if (!Number.isFinite(number)) return String(value);
  return number
    .toLocaleString("en-US")
    .replace(/\d/g, (digit) => PERSIAN_DIGITS[digit]);
}
