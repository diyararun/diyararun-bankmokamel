"""لایه‌ی دوم از استراتژی دفاعی چهار-لایه‌ای در برابر فشار سرور ناشی از
پردازش تصاویر محصول (نگاه کنید به «نشست ۳۷» در docs/backend/progress-log.md
برای توضیح کامل چهار لایه). لایه‌ی اول (nginx) خارج از این کدبیس است و
لایه‌ی سوم خودِ Pillow است (ProductImage.normalize_image در models.py) —
این فایل فقط لایه‌ی دوم است: چند بررسیِ ارزان که قبل از رسیدن فایل به
پردازش سنگین Pillow (thumbnail/paste/re-encode) اجرا می‌شوند، تا فایل‌های
خراب، جعلی یا بیش‌ازحد بزرگ اصلاً به آن پردازش نرسند.

هرچه این‌جا رد شود، هرگز RAM/CPU سرور را برای پردازش کامل Pillow اشغال
نمی‌کند — دقیقاً هدفی که این لایه برایش اضافه شده.
"""

from django import forms
from PIL import Image, UnidentifiedImageError

# قبل از این‌که فایل اصلاً به Pillow برسد رد می‌شود — این ارزان‌ترین و
# زودترین بررسی است (فقط به Content-Length نیاز دارد، نه باز کردن فایل).
MAX_UPLOAD_BYTES = 3 * 1024 * 1024  # ۳ مگابایت

# سقف تعداد کل پیکسل‌ها، *قبل* از این‌که Pillow واقعاً محتوای تصویر را
# دیکد کند. عمداً جدا از محافظت داخلی خودِ Pillow
# (PIL.Image.MAX_IMAGE_PIXELS، پیش‌فرض ~۸۹ مگاپیکسل) نگه داشته شده،
# چون آن محافظت فقط یک *هشدار* صادر می‌کند نه خطا — خطای واقعی
# (DecompressionBombError) فقط روی دوبرابرِ آن آستانه (~۱۷۹ مگاپیکسل)
# صادر می‌شود، یعنی یک تصویر ۸۰ مگاپیکسلی بدون هیچ خطایی پردازش می‌شود
# و حافظه‌ی زیادی می‌گیرد. چون خروجی نهایی هرگز از
# PRODUCT_IMAGE_CANVAS_SIZE (۱۰۰۰×۱۰۰۰، در models.py) بزرگ‌تر نمی‌شود،
# پذیرفتن ورودی‌های چندین‌برابر بزرگ‌تر هیچ توجیهی ندارد.
MAX_PIXELS = 30_000_000  # تقریباً معادل یک تصویر مربعیِ ۵۵۰۰×۵۵۰۰

# حالت‌های رنگی‌ای که ProductImage.normalize_image (در models.py) بلد است
# درست پردازش کند: RGB/L/CMYK مستقیم به RGB تبدیل می‌شوند؛
# RGBA/LA/P-با-شفافیت روی پس‌زمینه‌ی سفید ترکیب می‌شوند. هر حالت دیگری
# (مثلاً "1" تک‌بیتی یا حالت‌های تخصصی I/F) اینجا رد می‌شود چون نه یک
# عکس واقعی محصول است، نه normalize_image برایش تست شده.
ALLOWED_MODES = {"RGB", "RGBA", "L", "LA", "P", "CMYK"}


def validate_image_before_pillow(uploaded_file):
    """اگر فایل آپلودشده یکی از این مشکلات را داشته باشد ValidationError
    می‌دهد؛ در غیر این صورت چیزی برنمی‌گرداند و فایل را با اشاره‌گر روی
    صفر برای مرحله‌ی بعدی (ProductImage.normalize_image) آماده می‌گذارد.

    نکته درباره‌ی تشخیص نوع فایل واقعی: به‌جای اعتماد به پسوند نام فایل
    یا اضافه‌کردن یک وابستگی‌ی جدید به پروژه (مثل filetype یا
    python-magic)، از خودِ Pillow استفاده می‌کنیم — Image.open() محتوای
    واقعی فایل (magic bytes سرآیند فایل) را می‌خواند، نه پسوندش را؛ پس
    یک فایل .txt که فقط نامش به .jpg تغییر کرده همین‌جا رد می‌شود، بدون
    نیاز به هیچ کتابخانه‌ی اضافه‌ای.
    """
    if uploaded_file.size > MAX_UPLOAD_BYTES:
        raise forms.ValidationError(
            f"حجم تصویر نباید بیشتر از {MAX_UPLOAD_BYTES // (1024 * 1024)} مگابایت باشد."
        )

    try:
        uploaded_file.seek(0)
        image = Image.open(uploaded_file)
        # verify() ساختار فایل را می‌سنجد (فایل واقعاً یک تصویر سالم است،
        # نه یک فایل جعلی/خراب با سرآیند تصادفی) — طبق مستندات Pillow،
        # بعد از verify() خودِ همین شیء image برای هیچ استفاده‌ی دیگری
        # (حتی خواندن size) قابل‌اعتماد نیست، پس چند خط پایین‌تر دوباره
        # از صفر باز می‌شود.
        image.verify()
    except (UnidentifiedImageError, OSError, ValueError):
        raise forms.ValidationError("فایل انتخاب‌شده یک تصویر معتبر نیست یا آسیب‌دیده است.")

    uploaded_file.seek(0)
    image = Image.open(uploaded_file)

    width, height = image.size
    if width * height > MAX_PIXELS:
        raise forms.ValidationError(
            "ابعاد تصویر بیش‌ازحد بزرگ است؛ لطفاً تصویری با ابعاد کوچک‌تر انتخاب کنید."
        )

    if image.mode not in ALLOWED_MODES:
        raise forms.ValidationError("فرمت رنگی این تصویر پشتیبانی نمی‌شود.")

    uploaded_file.seek(0)
