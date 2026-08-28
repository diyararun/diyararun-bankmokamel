# بانک مکمل — نسخه ماژولار (Django + Vite + Tailwind)

## معماری
جنگو تمپلیت‌ها را رندر می‌کند (`{% %}` داخل HTML). Vite فقط برای باندل کردن
CSS/JS استفاده می‌شود و از طریق پکیج `django-vite` به جنگو وصل است.

```
backend/    → پروژه‌ی جنگو (اپ‌های accounts و store)
frontend/   → پروژه‌ی Vite (Tailwind + JS ماژولار)
```

## راه‌اندازی (حالت توسعه)

### ۱. فرانت‌اند (Vite)
```bash
cd frontend
npm install
npm run dev        # روی localhost:5173 بالا می‌آید (Hot Reload)
```

### ۲. بک‌اند (Django)
در یک ترمینال جدا:
```bash
cd backend
python -m venv venv
source venv/bin/activate      # ویندوز: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser   # اختیاری، برای پنل ادمین
python manage.py runserver
```
سپس آدرس `http://localhost:8000` را باز کنید. تا زمانی که سرور Vite (مرحله ۱)
روشن است، هر تغییری در فایل‌های `frontend/src` بلافاصله در مرورگر اعمال می‌شود.

## راه‌اندازی (حالت Production)
```bash
cd frontend && npm run build     # خروجی در frontend/dist ساخته می‌شود
cd ../backend
# در settings.py مقدار DEBUG=False کنید تا django-vite به‌جای dev
# server از frontend/dist/.vite/manifest.json بخواند
python manage.py collectstatic
python manage.py runserver
```

## ورود / ثبت‌نام (OTP)
در حالت توسعه، کد تایید همیشه `11111` است (بدون نیاز به سرویس پیامک واقعی).
محل اتصال به سرویس پیامک واقعی: `backend/accounts/models.py` → متد
`PhoneOTP.generate_for`.

## ویژگی پروفایل کاربر
- وقتی کاربر وارد شده باشد، دکمه‌ی «ورود | ثبت‌نام» در هدر با آیکون پروفایل
  (نام کاربر + دراپ‌داون) جایگزین می‌شود — هم در نسخه‌ی دسکتاپ
  (`templates/partials/header_main.html`) و هم موبایل
  (`templates/partials/mobile_menu.html`).
- صفحه‌ی پروفایل: `templates/pages/profile.html` — فرم ویرایش نام، نام‌خانوادگی،
  ایمیل و کد ملی (شماره موبایل غیرقابل‌ویرایش است).
- ویو مربوطه: `backend/accounts/views.py` → `profile_view`.

## نکات و قدم‌های بعدی پیشنهادی
- **سبد خرید**: در حال حاضر فقط در حافظه‌ی مرورگر است (`frontend/src/js/cartDrawer.js`)
  و با رفتن به صفحه‌ی دیگر خالی می‌شود — دقیقاً همان رفتار نسخه‌ی اولیه‌ی
  استاتیک. برای پایدارسازی بین صفحات/رفرش باید به یک API جنگو یا `localStorage`
  وصل شود.
- **محصولات**: فعلاً داده‌ی محصولات داخل تمپلیت‌ها هاردکد است. قدم بعدی طبیعی
  ساخت مدل `Product` در اپ `store` و اتصال `products.html` / `product_detail.html`
  به دیتابیس است (لینک «مشاهده محصول» فعلاً به `slug='demo'` ثابت اشاره می‌کند).
- **چک‌اوت**: آیتم‌های نمایش داده‌شده در صفحه‌ی تسویه‌حساب نمونه (hardcoded) هستند؛
  باید به سبد خرید واقعی/سفارش وصل شوند.
