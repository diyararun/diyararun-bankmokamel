// فرم افزودن/ویرایش «آدرس‌های من» (apps.accounts.forms.AddressForm).
//
// نشست ۳۵: همان اعتبارسنجی سمت کلاینت («فقط حرف فارسی» برای نام
// تحویل‌گیرنده/استان/شهر، «فقط رقم» برای شماره/کدپستی/پلاک/واحد) که فرم
// تسویه‌حساب داشت، حالا اینجا هم هست — همان ماژول مشترک
// (../fieldValidation.js)، فقط با آی‌دی‌های فیلدهای همین فرم. برخلاف
// فرم تسویه‌حساب، این فرم فیلد national_code ندارد (کد ملی مخصوص فاکتور
// خرید است، نه آدرس)، برای همین در لیست digits نیامده.
import { initFieldValidation } from "../fieldValidation.js";

document.addEventListener("DOMContentLoaded", () => {
  initFieldValidation({
    persian: ["id_full_name", "id_province", "id_city"],
    digits: ["id_phone", "id_postal_code", "id_plaque", "id_unit"],
  });
});
