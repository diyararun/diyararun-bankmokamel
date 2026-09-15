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
      // نشست ۴۰: سایزِ (اندازه‌ی) فونت‌ها — جدا از fontFamily بالا که فقط
      // «نوع» فونت را کنترل می‌کند. هر کلید این‌جا یک نقشِ مشخص در طراحی
      // سایت است (نه یک عددِ دلخواه)؛ مقدارِ واقعیِ px هرکدام در
      // frontend/src/css/main.css (بخش «اندازه‌ی فونت‌ها») تعریف شده و از
      // همان‌جا تغییر می‌کند. line-height هرکدام همان مقدارِ پیش‌فرضِ
      // خودِ Tailwind برای همان پله‌ی قدیمی است (تا فقط سایز عوض شود، نه
      // فاصله‌ی خطوط) — به‌جز کلاس‌های caption-10/11 که از ابتدا (وقتی
      // به‌صورت text-[10px]/text-[11px] نوشته می‌شدند) بدون line-height
      // مخصوص بودند و همین‌طور مانده‌اند.
      fontSize: {
        // ---------- تیتر اصلیِ Hero (فقط صفحه‌ی اول، همان یک h1) ----------
        // در سه اندازه‌ی متفاوت برای موبایل/تبلت/دسکتاپ (قبلاً text-4xl/
        // sm:text-6xl/lg:text-7xl) — کلاس‌ها: text-hero-mobile،
        // sm:text-hero-tablet، lg:text-hero-desktop
        "hero-mobile": ["var(--font-size-hero-mobile)", "2.5rem"],
        "hero-tablet": ["var(--font-size-hero-tablet)", "1"],
        "hero-desktop": ["var(--font-size-hero-desktop)", "1"],
        // ---------- «سرتیر»ها: h2/h3/h4 در تمام صفحات ----------
        // هرکدام معادلِ یکی از پله‌های قدیمیِ Tailwind است؛ نامِ کلاس
        // یعنی «تیترِ فلان‌سایز» — نه این‌که فقط یک‌جای خاص استفاده شود.
        "heading-48": ["var(--font-size-heading-48)", "1"], // تیترِ صفحه‌ی درباره‌ما (about.html) — قبلاً text-5xl
        "heading-30": ["var(--font-size-heading-30)", "2.25rem"], // تیترِ hero صفحه‌ی درباره‌ما/تماس، حالتِ sm به بعد — قبلاً text-3xl
        "heading-24": ["var(--font-size-heading-24)", "2rem"], // سرتیرِ اصلیِ بخش‌ها در صفحه‌ی اول (دسته‌بندی‌ها، محصولات پرفروش، ...) — قبلاً text-2xl
        "heading-20": ["var(--font-size-heading-20)", "1.75rem"], // تیترِ نامِ محصول در کارت‌های محصولِ صفحه‌ی اول — قبلاً text-xl
        "heading-18": ["var(--font-size-heading-18)", "1.75rem"], // تیترِ کوچک‌ترِ بخش‌ها (فرم تماس، ویژگی‌های «چرا بانک مکمل») — قبلاً text-lg
        "heading-16": ["var(--font-size-heading-16)", "1.5rem"], // تیترِ نامِ محصول در کارت‌های فشرده‌تر — قبلاً text-base
        "heading-14": ["var(--font-size-heading-14)", "1.25rem"], // تیترِ زیرـبخش‌ها (کارت‌های ویژگی، دسته‌بندی، مخاطب) — قبلاً text-sm
        "heading-12": ["var(--font-size-heading-12)", "1rem"], // کوچک‌ترین تیتر (مثلاً نامِ کاربر در نظرات مشتریان) — قبلاً text-xs
        // ---------- متن‌های عادیِ سایت (پاراگراف، لیبل، دکمه و ...) ----------
        // این سه کلید، کلیدهای اصلیِ خودِ Tailwind را بازتعریف می‌کنند —
        // یعنی نیازی به کلاسِ جدید در قالب‌ها نبود: همین حالا هر جای
        // سایت که از text-xs/text-sm/text-base استفاده می‌کند (اکثرِ
        // متن‌های سایت)، خودکار از این متغیرها تبعیت می‌کند.
        xs: ["var(--font-size-body-12)", "1rem"], // اکثرِ متن‌های ریزِ سایت — قبلاً همیشه ۱۲px
        sm: ["var(--font-size-body-14)", "1.25rem"], // متنِ معمولیِ سایت — قبلاً همیشه ۱۴px
        base: ["var(--font-size-body-16)", "1.5rem"], // متنِ استاندارد/پیش‌فرضِ سایت — قبلاً همیشه ۱۶px
        // ---------- کپشن‌های خیلی ریز (قبلاً مقدارِ دلخواهِ text-[..px]) ----------
        // این دو مقدار قبلاً هیچ‌جای دیگرِ Tailwind تعریف نشده بودند
        // (کدنویس هر بار مستقیم می‌نوشت text-[10px] یا text-[11px])؛
        // حالا با متغیر کنترل می‌شوند، مثلِ بقیه.
        "caption-10": "var(--font-size-caption-10)", // ریزنویسِ زیرِ لیبل‌ها/بج‌های کوچک — قبلاً text-[10px]
        "caption-11": "var(--font-size-caption-11)", // ریزنویسِ کمی بزرگ‌تر (شماره تماس، آدرس در فوتر/فرم‌ها) — قبلاً text-[11px]
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