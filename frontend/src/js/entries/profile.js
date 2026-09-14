// صفحه‌ی پروفایل کاملاً سمت سرور (جنگو) رندر و ذخیره می‌شود؛ این فایل
// جای آماده برای رفتارهای آینده (مثلاً آپلود آواتار) است.
//
// نشست ۳۵: همان اعتبارسنجی سمت کلاینت («فقط حرف فارسی» برای نام/نام
// خانوادگی، «فقط رقم» برای کد ملی) که فرم تسویه‌حساب داشت، حالا اینجا
// هم هست — همان ماژول مشترک (../fieldValidation.js)، فقط با آی‌دی‌های
// فیلدهای همین فرم (apps.accounts.forms.ProfileForm).
import { initFieldValidation } from "../fieldValidation.js";

document.addEventListener("DOMContentLoaded", () => {
  initFieldValidation({
    persian: ["id_first_name", "id_last_name"],
    digits: ["id_national_code"],
  });
});
