// اعتبارسنجی سمت کلاینت مشترک بین فرم تسویه‌حساب (checkout.js)، فرم
// ویرایش اطلاعات حساب کاربری (profile.js)، و فرم آدرس‌های من
// (addressForm.js). این منطق قبلاً فقط داخل checkout.js بود؛ چون هر سه
// فرم دقیقاً به همان دو قانون نیاز دارند («فقط حرف فارسی» برای نام/
// استان/شهر، «فقط رقم» برای شماره/کدپستی/پلاک/واحد)، یک‌بار اینجا
// نوشته شده تا کپی‌پیست سه‌باره نشود — دقیقاً همان استدلالی که
// apps.store.validators سمت بک‌اند را یک‌جا کرد.
//
// یادآوری مهم (از خودِ checkout.js قبلی): این فقط برای تجربه‌ی کاربری
// (UX) است — جلوگیری از تایپ یک کاراکتر اشتباه، نه یک لایه‌ی امنیتی.
// تنها منبع مورد اعتماد برای صحت داده همان clean_<field>های سمت بک‌اند
// (apps.store.validators) هستند: کاربری که جاوااسکریپت را غیرفعال کند،
// یا مستقیماً به سرور پست بزند، همچنان توسط بک‌اند بررسی می‌شود.

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

// fieldIds.persian: آی‌دی‌های فیلدهایی که باید فقط حرف فارسی بگیرند
// (مثلاً id_full_name، id_first_name، id_province، id_city).
// fieldIds.digits: آی‌دی‌های فیلدهایی که باید فقط رقم بگیرند (مثلاً
// id_phone، id_national_code، id_postal_code، id_plaque، id_unit).
// آی‌دی‌ها همان‌طور که Django برای هر فیلد فرم می‌سازد (id_<نام فیلد> —
// پیش‌فرض ویجت‌های جنگو)، پس هر فرم فقط لیست فیلدهای خودش را می‌دهد.
export function initFieldValidation({ persian = [], digits = [] } = {}) {
  persian.forEach((id) => bindField(id, onlyPersianLettersKeydown, sanitizePersianInput));
  digits.forEach((id) => bindField(id, onlyDigitsKeydown, sanitizeDigitsInput));
}
