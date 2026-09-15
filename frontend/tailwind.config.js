/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "../backend/templates/**/*.html",
    // Page templates now live inside each app (apps/catalog/templates/,
    // apps/store/templates/, apps/accounts/templates/, apps/orders/templates/...)
    // instead of the single shared backend/templates/ folder — this glob
    // covers all of them.
    "../backend/apps/*/templates/**/*.html",
    "./src/**/*.js",
  ],
  theme: {
    extend: {
      // نشست ۳۹: قبلاً اسم فونت («Vazirmatn») مستقیم همین‌جا نوشته شده
      // بود — تنها جای کل پروژه که فونت واقعاً تعیین می‌شد، ولی هنوز هم
      // یعنی برای تغییرِ فونت باید سراغ کد جنگو (این فایل، بخش build)
      // می‌رفتید. حالا این‌جا فقط دو *نقشِ* فونت (عنوان/متن) را به دو
      // متغیر CSS وصل می‌کند — خودِ اسمِ واقعیِ فونت‌ها در یک‌جا، داخل
      // frontend/src/css/main.css (بخش :root)، تعریف شده‌اند. برای عوض‌
      // کردنِ فونت کل سایت، دیگر لازم نیست این فایل را باز کنید — همان
      // دو متغیر در main.css کافی است.
      fontFamily: {
        // پیش‌فرضِ همه‌ی متن‌های سایت — از طریق کلاس font-sans که روی
        // body در base.html قرار دارد (نگاه کنید به آن فایل)، و چون
        // Tailwind خودش fontFamily.sans را پیش‌فرضِ کل صفحه هم می‌داند،
        // هر جایی که هیچ کلاس فونتی صریح ننوشته باشد هم همین را به ارث
        // می‌برد — یعنی نیازی نیست این کلاس را روی تک‌تک تگ‌های متنی
        // (پاراگراف، span و ...) در سراسر قالب‌ها تکرار کنیم.
        sans: ["var(--font-text)"],
        // فقط برای عنوان‌ها (h1 تا h6) — کلاس font-title، که در همین
        // نشست روی تمام تگ‌های h1-h6 در تمام صفحات اضافه شده.
        title: ["var(--font-title)"],
      },
      colors: {
        brandRed: "#DC2626",
        brandDark: "#0F172A",
        brandGray: "#F8FAFC",
      },
      animation: {
        "infinite-scroll": "infinite-scroll 25s linear infinite",
        "bounce-short": "bounce-short 0.3s ease-in-out",
      },
      keyframes: {
        "infinite-scroll": {
          "0%": { transform: "translateX(0)" },
          "100%": { transform: "translateX(100%)" },
        },
        "bounce-short": {
          "0%, 100%": { transform: "scale(1)" },
          "50%": { transform: "scale(1.3)" },
        },
      },
    },
  },
  plugins: [],
};