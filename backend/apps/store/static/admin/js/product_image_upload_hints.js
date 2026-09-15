/**
 * لایه‌ی چهارم (اختیاری) از استراتژی چهار-لایه‌ای دفاعیِ آپلود تصویر
 * محصول — نگاه کنید به apps/catalog/validators.py برای لایه‌ی دوم
 * (اعتبارسنجیِ واقعی و الزامی، قبل از Pillow) و
 * ProductImage._encode_within_size_cap در apps/catalog/models.py برای
 * لایه‌ی سوم (خودِ Pillow)؛ توضیح کامل هر چهار لایه در
 * docs/backend/progress-log.md، نشست ۳۷.
 *
 * این اسکریپت هیچ اعتبارسنجیِ واقعی انجام نمی‌دهد و جای هیچ‌کدام از دو
 * لایه‌ی سرور را نمی‌گیرد — همه‌ی بررسی‌های الزامی همچنان آن‌جا انجام
 * می‌شوند. این فقط یک هشدارِ زودهنگام و غیرمسدودکننده است: به فروشنده
 * *قبل* از آپلود واقعی (و رفت‌وبرگشت شبکه) بگوید این فایل به‌احتمال زیاد
 * توسط سرور رد خواهد شد، تا زودتر فایل مناسب‌تری انتخاب کند. کاربر
 * همچنان می‌تواند با همین فایل فرم را ارسال کند؛ خطای نهایی و قطعی همان
 * چیزی است که سرور (لایه‌ی دوم) برمی‌گرداند.
 *
 * فقط روی اینپوت‌های فایلِ اینلاینِ «تصاویر محصول» (#images-group —
 * پیشوند پیش‌فرض جنگو برای این فرم‌ست از related_name="images" روی
 * ProductImage.product می‌آید) فعال می‌شود، نه هر اینپوت فایلی در کل
 * پنل ادمین؛ چون فقط همین یکی از این سقف‌های خاص (حجم/ابعاد) در سمت
 * سرور برخوردار است — آیکون دسته‌بندی یا لوگوی برند این قوانین را
 * ندارند.
 *
 * از event delegation روی خودِ #images-group استفاده می‌شود (نه بایند
 * مستقیم روی هر input در زمان بارگذاری صفحه)، چون با کلیک «افزودن یکی
 * دیگر» جنگو ادمین ردیف‌ها (و اینپوت‌های فایل جدید) را پویا اضافه
 * می‌کند؛ اینپوتی که هنوز در صفحه وجود ندارد نمی‌تواند مستقیماً
 * listener بگیرد.
 */
(function () {
  "use strict";

  // این دو عدد باید با MAX_UPLOAD_BYTES/MAX_PIXELS در
  // apps/catalog/validators.py هماهنگ بمانند. سرور تنها منبع واقعی و
  // الزام‌آور است؛ این‌جا فقط یک کپی برای هشدار زودهنگام است — اگر یکی
  // از آن دو عدد آن‌جا عوض شد، این دو عدد هم باید دستی به‌روزرسانی شوند.
  var MAX_UPLOAD_BYTES = 3 * 1024 * 1024;
  var MAX_PIXELS = 30 * 1000 * 1000;
  var HINT_CLASS = "fa-image-upload-hint";

  function clearHint(input) {
    var existing = input.parentElement.querySelector("." + HINT_CLASS);
    if (existing) {
      existing.remove();
    }
  }

  function showHint(input, message) {
    clearHint(input);
    var hint = document.createElement("p");
    hint.className = HINT_CLASS;
    hint.style.color = "#c0392b";
    hint.style.fontSize = "11px";
    hint.style.margin = "4px 0 0";
    hint.textContent = message;
    input.parentElement.appendChild(hint);
  }

  function checkDimensions(input, file) {
    var objectUrl = URL.createObjectURL(file);
    var probe = new Image();
    probe.onload = function () {
      URL.revokeObjectURL(objectUrl);
      if (probe.naturalWidth * probe.naturalHeight > MAX_PIXELS) {
        showHint(input, "ابعاد این تصویر بیش‌ازحد بزرگ است و توسط سرور رد خواهد شد.");
      }
    };
    probe.onerror = function () {
      // فایلی که مرورگر نتواند به‌عنوان تصویر دیکد کند، به هر حال با
      // بررسی نوع فایل بالاتر (قبل از این تابع) قبلاً هشدار گرفته —
      // این‌جا کار اضافه‌ای لازم نیست.
      URL.revokeObjectURL(objectUrl);
    };
    probe.src = objectUrl;
  }

  function checkFile(input) {
    clearHint(input);
    var file = input.files && input.files[0];
    if (!file) {
      return;
    }

    if (file.type.indexOf("image/") !== 0) {
      showHint(input, "این فایل یک تصویر نیست و توسط سرور رد خواهد شد.");
      return;
    }

    if (file.size > MAX_UPLOAD_BYTES) {
      showHint(
        input,
        "حجم این فایل (" +
          (file.size / (1024 * 1024)).toFixed(1) +
          " مگابایت) از سقف مجاز (۳ مگابایت) بیشتر است و توسط سرور رد خواهد شد."
      );
      return;
    }

    checkDimensions(input, file);
  }

  document.addEventListener("DOMContentLoaded", function () {
    var group = document.getElementById("images-group");
    if (!group) {
      return;
    }
    group.addEventListener("change", function (event) {
      if (event.target && event.target.matches('input[type="file"]')) {
        checkFile(event.target);
      }
    });
  });
})();
