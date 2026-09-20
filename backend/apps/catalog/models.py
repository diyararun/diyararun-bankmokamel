import io
import os

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import models, transaction
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django_jalali.db import models as jmodels
from PIL import Image, ImageChops, ImageOps

from .validators import validate_image_before_pillow

# Rendered as an admin radio widget (two options) instead of the default
# checkbox for is_main_category/is_popular below — see
# CategoryAdmin.radio_fields in apps/catalog/admin.py. Django admin only
# switches a field to a radio widget when the field has `choices` *and*
# its name is listed in radio_fields, so a plain BooleanField (no
# choices) needs this explicit choice list even though both options are
# still just True/False.
BOOLEAN_RADIO_CHOICES = ((True, "بله"), (False, "خیر"))


class Category(models.Model):
    """Product category (e.g. 'پروتئین', 'کراتین'). Self-referential so
    subcategories can be introduced later without a schema change."""

    name = models.CharField("نام دسته‌بندی", max_length=100)
    slug = models.SlugField("اسلاگ", max_length=120, unique=True)
    icon = models.ImageField(
        "آیکون", upload_to="categories/", blank=True, null=True,
        help_text="در کارت‌های دسته‌بندی صفحه‌ی اصلی نمایش داده می‌شود",
    )
    parent = models.ForeignKey(
        "self",
        verbose_name="دسته‌بندی والد",
        null=True,
        blank=True,
        related_name="children",
        on_delete=models.SET_NULL,
    )
    is_active = models.BooleanField("فعال", default=True)
    # "دسته‌بندی اصلی" — یک برچسب مستقل از parent، تا فروشنده خودش تعیین
    # کند کدام دسته‌بندی‌های سطح‌بالا واقعاً در سایدبار «همه‌ی دسته‌بندی‌ها»
    # نمایش داده شوند (به‌جای این‌که هر دسته‌ی بدون والد به‌طور خودکار
    # آن‌جا ظاهر شود). فقط دسته‌بندی‌های بدون والد می‌توانند این برچسب را
    # داشته باشند — clean() پایین همین را بررسی می‌کند.
    is_main_category = models.BooleanField(
        "دسته‌بندی اصلی",
        default=False,
        choices=BOOLEAN_RADIO_CHOICES,
        help_text="فقط دسته‌بندی‌های بدون والد قابل انتخاب به‌عنوان دسته‌بندی اصلی هستند.",
    )
    # زیرمجموعه‌ی «دسته‌بندی اصلی»: تا ۸ تای این‌ها در صفحه‌ی اصلی، بخش
    # «دسته‌بندی‌های محبوب» نمایش داده می‌شوند (store/views.py::IndexView).
    is_popular = models.BooleanField(
        "دسته‌بندی محبوب",
        default=False,
        choices=BOOLEAN_RADIO_CHOICES,
        help_text="حداکثر ۶ دسته‌بندی محبوب در صفحه‌ی اصلی نمایش داده می‌شود؛ فقط برای دسته‌بندی‌های اصلی قابل انتخاب است.",
    )

    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        # این دو قانون عمداً این‌جا (روی مدل) هستند نه فقط در ادمین، تا هر
        # مسیر دیگری که بعداً Category را می‌سازد/ویرایش می‌کند (مثلاً یک
        # اسکریپت import) هم همین قاعده را رعایت کند.
        if self.is_main_category and self.parent_id:
            raise ValidationError(
                {"is_main_category": "فقط دسته‌بندی‌های بدون والد می‌توانند دسته‌بندی اصلی باشند."}
            )
        if self.is_popular and not self.is_main_category:
            raise ValidationError(
                {"is_popular": "دسته‌بندی محبوب فقط برای دسته‌بندی‌های اصلی قابل انتخاب است."}
            )

    @property
    def active_product_count(self):
        return self.products.filter(is_active=True).count()


class Brand(models.Model):
    """Product manufacturer/brand (e.g. 'اپتیموم نوتریشن')."""

    name = models.CharField("نام برند", max_length=100)
    slug = models.SlugField("اسلاگ", max_length=120, unique=True)
    logo = models.ImageField("لوگو", upload_to="brands/", blank=True, null=True)
    description = models.TextField("توضیحات", blank=True)
    is_active = models.BooleanField("فعال", default=True)

    class Meta:
        verbose_name = "برند"
        verbose_name_plural = "برندها"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Flavor(models.Model):
    """Reusable flavor option (e.g. 'شکلات دبل', 'وانیل بستنی').

    A single lookup table so the same flavor name is reused consistently
    across products instead of being retyped as free text every time.
    """

    name = models.CharField("نام طعم", max_length=50, unique=True)

    class Meta:
        verbose_name = "طعم"
        verbose_name_plural = "طعم‌ها"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    """A sellable product. Price, stock and flavor/weight combinations
    live on ProductVariant below — this model only holds the shared
    marketing/description content for the product as a whole.
    """

    FORM_TYPE_CHOICES = [
        ("powder", "پودر"),
        ("tablets", "قرص / کپسول"),
        ("liquid", "مایع / شات"),
    ]

    category = models.ForeignKey(
        Category, verbose_name="دسته‌بندی", related_name="products", on_delete=models.PROTECT
    )
    brand = models.ForeignKey(
        Brand, verbose_name="برند", related_name="products", on_delete=models.PROTECT
    )
    name = models.CharField("نام محصول", max_length=200)
    slug = models.SlugField("اسلاگ", max_length=220, unique=True)
    short_description = models.CharField(
        "توضیح کوتاه", max_length=300, blank=True, help_text="در کارت محصولات نمایش داده می‌شود"
    )
    description = models.TextField("توضیحات کامل", blank=True)
    usage_instructions = models.TextField("نحوه مصرف", blank=True)
    form_type = models.CharField(
        "نوع/فرم مکمل", max_length=20, choices=FORM_TYPE_CHOICES, blank=True,
        help_text="برای فیلتر «نوع مکمل» در صفحه‌ی محصولات استفاده می‌شود",
    )
    is_active = models.BooleanField("فعال (قابل نمایش)", default=True)
    # این دو، همان چیزی هستند که صفحه‌ی اصلی برای بخش‌های «محصولات
    # پرفروش» و «تخفیفات ویژه و شگفت‌انگیز» می‌خواند (store/views.py::
    # IndexView) — قبلاً آن دو بخش صرفاً «جدیدترین محصولات» را نشان
    # می‌دادند، نه واقعاً پرفروش‌ترین/بهترین‌تخفیف را. عمداً یک چک‌باکس
    # ساده روی خودِ محصول‌اند (نه یک مدل/رابطه‌ی جدا)، و در ادمین با
    # list_editable روی همین لیست فعلی محصولات علامت زده می‌شوند — نه با
    # یک فیلد انتخابی جدا برای هر کدام از صدها محصول، و نه یک صفحه‌ی
    # جست‌وجوی جدید: فروشنده در همان لیست محصولات سرچ/فیلتر می‌کند و
    # فقط تیک همان چند محصول را می‌زند.
    is_best_seller = models.BooleanField(
        "پرفروش",
        default=False,
        help_text="در صفحه‌ی اصلی، بخش «محصولات پرفروش» را همین‌ها (حداکثر ۸ تا) پر می‌کنند.",
    )
    is_featured_deal = models.BooleanField(
        "تخفیف ویژه/شگفت‌انگیز",
        default=False,
        help_text="در صفحه‌ی اصلی، بخش «تخفیفات ویژه و شگفت‌انگیز» را همین‌ها (حداکثر ۸ تا) پر می‌کنند.",
    )
    created_at = jmodels.jDateTimeField("تاریخ ایجاد", auto_now_add=True)
    updated_at = jmodels.jDateTimeField("تاریخ ویرایش", auto_now=True)

    class Meta:
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    @property
    def active_variants(self):
        return self.variants.filter(is_active=True)

    @property
    def default_variant(self):
        """The variant shown by default on the product card/detail page —
        the cheapest active, in-stock variant, falling back to the
        cheapest active variant if none are in stock."""
        in_stock = self.active_variants.filter(stock__gt=0).order_by("price")
        return in_stock.first() or self.active_variants.order_by("price").first()

    @property
    def average_rating(self):
        approved = self.reviews.filter(is_approved=True)
        return approved.aggregate(models.Avg("rating"))["rating__avg"]


# Every product image is normalized to a square canvas of this size (px)
# before it's ever saved to disk — see ProductImage.save() below. Chosen
# to be large enough to still look sharp on a product-detail zoom, small
# enough that the resulting JPEG stays tiny — usually well under 100KB for
# an ordinary clean product photo, and never above
# PRODUCT_IMAGE_MAX_OUTPUT_BYTES below even for an unusually complex one
# (see _encode_within_size_cap()) — see the docstring on save() for why
# this matters for page speed, not just layout consistency.
PRODUCT_IMAGE_CANVAS_SIZE = 1000
PRODUCT_IMAGE_JPEG_QUALITY = 85
# How much of the final square canvas the product itself should fill,
# after normalize_image()'s own whitespace-trimming step below — the
# rest is even margin split between every side. See _trim_white_margin()
# for why this trimming step exists at all.
#
# This is the ONE place that controls how "zoomed in" every product photo
# looks — homepage, product listing, and product-detail page all read the
# exact same stored file, so raising or lowering this single number is
# reflected everywhere at once, with no template changes needed. Keep it
# below 1.0 (a small margin on every side reads as an intentional product
# shot; exactly 1.0 would touch the canvas edges and can look like a bad
# crop). نشست ۳۳: از ۰.۸۶ به ۰.۹۴ افزایش یافت چون محصولات کمی دورتر از
# حد دلخواه دیده می‌شدند؛ برای تغییر دوباره‌ی میزان زوم در آینده، فقط
# همین عدد را عوض کنید و دستور مدیریتی زیر را دوباره اجرا کنید:
#   python manage.py normalize_product_images
PRODUCT_IMAGE_CONTENT_RATIO = 0.9
# A pixel counts as "background" during trimming only if it's within
# this much of pure white (0-255 per channel) — a hard difference-from-
# white check would also flag ordinary JPEG compression noise in an
# otherwise-white studio backdrop as "content" and defeat the trim.
PRODUCT_IMAGE_WHITE_MARGIN_THRESHOLD = 12
# نشست ۳۷ — لایه‌ی سوم از استراتژی چهار-لایه‌ای (نگاه کنید به
# apps/catalog/validators.py برای لایه‌ی دوم و به progress-log.md برای
# توضیح کامل هر چهار لایه): تا این‌جا هیچ سقف واقعی‌ای روی حجم خروجی
# نهایی وجود نداشت — کیفیت ثابت ۸۵ برای عکس‌های تمیز و ساده‌ی محصول
# معمولاً چند ده کیلوبایت خروجی می‌دهد، اما برای یک عکس شلوغ/پرجزئیات
# می‌تواند به چند صد کیلوبایت هم برسد (چون حجم JPEG به پیچیدگیِ بصریِ
# تصویر بستگی دارد، نه فقط ابعادش). save() پایین، بعد از اولین
# انکود، اگر خروجی از این سقف بیشتر بود، کیفیت را پله‌پله کم می‌کند و
# دوباره انکود می‌کند تا واقعاً زیر سقف بیاید — یعنی «حداکثر ۱۰۰-۱۵۰
# کیلوبایت» دیگر فقط یک انتظار تجربی نیست، یک تضمین است.
PRODUCT_IMAGE_MAX_OUTPUT_BYTES = 150 * 1024  # ۱۵۰ کیلوبایت
# پایین‌تر از این کیفیت، افت کیفیت بصری برای یک عکس فروشگاهی به‌وضوح
# نامناسب می‌شود — بهتر است یک عکس واقعاً غیرعادی (مثلاً یک بافت بسیار
# نویزی) کمی بیشتر از سقف بماند تا این‌که همه‌ی عکس‌ها را به‌خاطر یک
# مورد استثنایی زشت کنیم.
PRODUCT_IMAGE_MIN_JPEG_QUALITY = 50


class ProductImage(models.Model):
    """One image in a product's gallery. is_primary marks the image shown
    on product cards and as the default detail-page image.

    Whatever the seller uploads — any resolution, any aspect ratio, with
    or without transparency — save() below normalizes it to a fixed
    PRODUCT_IMAGE_CANVAS_SIZE x PRODUCT_IMAGE_CANVAS_SIZE white-padded
    square before it's written to disk. This is what makes every product
    card look consistent (see نشست ۲۱ in the progress log): the
    templates already show these images in a fixed-size box with
    object-contain (never cropped), but object-contain alone still let a
    tightly-framed photo look "bigger" than a loosely-framed one in the
    exact same box. Normalizing the stored file itself — instead of
    relying on every seller to crop/pad their photos consistently by hand
    — fixes that at the source, for every place this image is used
    (product cards, hero, the detail-page gallery), not just one section.

    نشست ۳۲: صرفاً مربع‌کردن کافی نبود — دو عکس با همان محصول ولی حاشیه‌ی
    سفید متفاوت (یکی محصول را تنگ فریم کرده، دیگری فضای خالی زیادی
    دورش گذاشته) باز هم داخل همان مربع، اندازه‌های به‌ظاهر متفاوتی به
    نظر می‌رسیدند — چون حاشیه‌ی خودِ عکس اصلی دست‌نخورده باقی می‌ماند.
    _trim_white_margin() پایین، قبل از قرار گرفتن روی بوم، این حاشیه‌ی
    سفید/تقریباً سفید را از هر عکسی می‌بُرد (چه پس‌زمینه‌ی سفید واقعی
    باشد، چه شفافیتی که همین‌جا به سفید تبدیل شده) تا محصول همیشه یک
    نسبت ثابت (PRODUCT_IMAGE_CONTENT_RATIO) از قاب نهایی را پر کند —
    نه هرچقدر که در عکس اصلی اتفاقی پر کرده بود.
    """

    product = models.ForeignKey(Product, verbose_name="محصول", related_name="images", on_delete=models.CASCADE)
    image = models.ImageField("تصویر", upload_to="products/%Y/%m/")
    alt_text = models.CharField("متن جایگزین", max_length=200, blank=True)
    is_primary = models.BooleanField("تصویر اصلی", default=False)
    order = models.PositiveIntegerField("ترتیب نمایش", default=0)

    class Meta:
        verbose_name = "تصویر محصول"
        verbose_name_plural = "تصاویر محصول"
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.product.name} - {self.order}"

    def clean(self):
        # نشست ۳۷ — لایه‌ی دوم از استراتژی چهار-لایه‌ای (نگاه کنید به
        # apps/catalog/validators.py): این بررسی‌ها ارزان‌اند و *قبل* از
        # این‌که Pillow واقعاً پردازش سنگین (thumbnail/paste/re-encode در
        # normalize_image پایین) را روی فایل انجام بدهد اجرا می‌شوند —
        # دقیقاً همان لحظه‌ای که فرم ادمین این مدل را قبل از ذخیره
        # اعتبارسنجی می‌کند (ModelForm._post_clean -> instance.full_clean)،
        # پس خطا به‌صورت طبیعی زیر فیلد «تصویر» در ادمین نمایش داده
        # می‌شود، نه یک خطای سرور ۵۰۰.
        super().clean()
        if self.image and not self.image._committed:
            validate_image_before_pillow(self.image)

    def save(self, *args, **kwargs):
        # `_committed` is False exactly when a NEW file was just assigned
        # to this field (an upload happening right now) — as opposed to
        # re-saving an existing row without touching the image (e.g.
        # editing alt_text). Without this check, every admin save would
        # re-process (and re-compress) an already-normalized image.
        old_image_name = None
        if self.image and not self.image._committed:
            # نشست ۳۸: فروشنده وقتی روی یک ردیفِ *موجود* تصویر جدیدی
            # انتخاب می‌کند، جنگو خودش هرگز فایل قدیمی را از روی دیسک پاک
            # نمی‌کند — فقط مقدار فیلد در دیتابیس عوض می‌شود، فایل قدیمی
            # همان‌جا روی media/ باقی می‌ماند، بی‌استفاده و برای همیشه.
            # چون فروشنده هیچ‌وقت مستقیم وارد پوشه‌ی media نمی‌شود که آن
            # را پیدا/پاک کند، این با هر جایگزینی یک فایل یتیمِ تکراری
            # اضافه می‌کند. برای همین، *قبل* از این‌که self.image با فایل
            # جدید جایگزین شود، نام فایل قدیمی را از خودِ دیتابیس
            # می‌خوانیم (نه از self، که همین الان فایل جدید را نگه
            # می‌دارد) تا بعد از ذخیره‌ی موفق فایل جدید بتوانیم آن را پاک
            # کنیم. self.pk خالی است یعنی این یک ردیف کاملاً جدید است، پس
            # اصلاً فایل قدیمی‌ای برای پاک‌کردن وجود ندارد.
            if self.pk:
                old_image_name = ProductImage.objects.filter(pk=self.pk).values_list("image", flat=True).first()
            self.image = self.normalize_image(self.image)
        super().save(*args, **kwargs)

        if old_image_name and old_image_name != self.image.name:
            # transaction.on_commit تضمین می‌کند که اگر ذخیره‌ی همین
            # درخواست به هر دلیلی rollback شود (مثلاً یک خطای دیگر در
            # همان تراکنش)، فایل قدیمی دست‌نخورده می‌ماند — حذف واقعی
            # فقط بعد از قطعی‌شدنِ ذخیره‌ی ردیف جدید در دیتابیس اتفاق
            # می‌افتد، نه زودتر.
            storage = self.image.storage
            transaction.on_commit(lambda: storage.delete(old_image_name))

    @staticmethod
    def normalize_image(uploaded_file):
        """Returns a ContentFile: the uploaded image resized to fit within
        PRODUCT_IMAGE_CANVAS_SIZE (never upscaled — a source image smaller
        than the canvas is centered as-is, since enlarging it would only
        blur it; ask sellers to upload at least ~800x800px), centered on a
        white square of exactly that size, re-encoded as JPEG.

        exif_transpose fixes the sideways/upside-down photos phone
        cameras commonly save (orientation stored as EXIF metadata,
        ignored by naive resizing). Transparent PNGs are flattened onto
        white rather than dropped (which would default to black).
        """
        image = Image.open(uploaded_file)
        image = ImageOps.exif_transpose(image)

        if image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
            image = image.convert("RGBA")
            white_background = Image.new("RGBA", image.size, (255, 255, 255, 255))
            image = Image.alpha_composite(white_background, image).convert("RGB")
        else:
            image = image.convert("RGB")

        image = ProductImage._trim_white_margin(image)

        content_size = round(PRODUCT_IMAGE_CANVAS_SIZE * PRODUCT_IMAGE_CONTENT_RATIO)
        image.thumbnail((content_size, content_size), Image.LANCZOS)

        canvas = Image.new("RGB", (PRODUCT_IMAGE_CANVAS_SIZE, PRODUCT_IMAGE_CANVAS_SIZE), (255, 255, 255))
        offset = (
            (PRODUCT_IMAGE_CANVAS_SIZE - image.width) // 2,
            (PRODUCT_IMAGE_CANVAS_SIZE - image.height) // 2,
        )
        canvas.paste(image, offset)

        buffer = ProductImage._encode_within_size_cap(canvas)

        original_name = os.path.splitext(os.path.basename(uploaded_file.name))[0]
        return ContentFile(buffer.getvalue(), name=f"{original_name}.jpg")

    @staticmethod
    def _trim_white_margin(image):
        """Crops away any plain white (or near-white) margin around the
        product, so the amount of "breathing room" in the final square
        depends only on PRODUCT_IMAGE_CONTENT_RATIO above — never on how
        tightly or loosely the seller happened to frame the original
        photo, and never on whether that margin started out as an actual
        white studio background or as transparency flattened onto white
        a few lines up. Without this, two photos of similarly-sized
        products could still land on the exact same size canvas and look
        like two different sizes — one "zoomed in", one "zoomed out" —
        purely because of how much empty space each seller's original
        photo happened to have around the product.

        Standard, dependency-free way to find "everything that isn't the
        background": diff the image against a solid white image of the
        same size, threshold that difference (a flat *near*-white JPEG
        backdrop is never perfectly (0,0,0) different from pure white —
        ordinary compression noise alone guarantees that — so a bare
        `getbbox()` on the raw difference would see that noise as
        "content" across the whole photo and trim nothing), then take the
        bounding box of what's left.

        Falls back to the untouched image whenever there's nothing to
        crop to (a blank/all-white photo, or a photo whose background
        isn't white/near-white at all — a lifestyle shot on a colored or
        textured background, say) rather than risk cropping into content
        it can't actually tell apart from background.
        """
        white = Image.new("RGB", image.size, (255, 255, 255))
        diff = ImageChops.difference(image, white).convert("L")
        diff = diff.point(lambda pixel: 255 if pixel > PRODUCT_IMAGE_WHITE_MARGIN_THRESHOLD else 0)
        bbox = diff.getbbox()
        return image.crop(bbox) if bbox else image

    @staticmethod
    def _encode_within_size_cap(canvas):
        """Encodes canvas as JPEG at PRODUCT_IMAGE_JPEG_QUALITY, then —
        only if that first encode came out heavier than
        PRODUCT_IMAGE_MAX_OUTPUT_BYTES — re-encodes at progressively lower
        quality until it fits (or PRODUCT_IMAGE_MIN_JPEG_QUALITY is
        reached, whichever comes first).

        JPEG size depends on how visually busy the image is, not just its
        pixel dimensions (نگاه کنید به توضیح بالای
        PRODUCT_IMAGE_MAX_OUTPUT_BYTES) — an ordinary clean product photo
        never even enters this loop; it only kicks in for the rare
        unusually noisy/complex source image, so the vast majority of
        images still get the full PRODUCT_IMAGE_JPEG_QUALITY.
        """
        quality = PRODUCT_IMAGE_JPEG_QUALITY
        buffer = io.BytesIO()
        canvas.save(buffer, format="JPEG", quality=quality, optimize=True)

        # `quality = max(quality - 10, MIN)` (نه صرفاً `quality -= 10`) عمداً
        # است: در غیر این صورت آخرین قدم می‌توانست کیفیت را از بالای سقف
        # مستقیم به *زیر* PRODUCT_IMAGE_MIN_JPEG_QUALITY ببرد (مثلاً از ۵۵
        # به ۴۵)، چون شرط حلقه با کیفیتِ *قبل* از کم‌شدن سنجیده می‌شود، نه
        # بعد از آن — این‌طور کیفیت هرگز از سقفِ پایین عبور نمی‌کند.
        while buffer.tell() > PRODUCT_IMAGE_MAX_OUTPUT_BYTES and quality > PRODUCT_IMAGE_MIN_JPEG_QUALITY:
            quality = max(quality - 10, PRODUCT_IMAGE_MIN_JPEG_QUALITY)
            buffer = io.BytesIO()
            canvas.save(buffer, format="JPEG", quality=quality, optimize=True)

        return buffer


@receiver(post_delete, sender=ProductImage)
def _delete_product_image_file_from_storage(sender, instance, **kwargs):
    """نشست ۳۸: هم‌خانواده‌ی همان مشکل «فایل یتیم» که در save() بالا حل
    شد — وقتی یک ردیف ProductImage پاک می‌شود (چه با تیک «حذف» در همان
    اینلاینِ «تصاویر محصول» در ادمین، چه به‌خاطر CASCADE وقتی خودِ محصول
    حذف می‌شود)، جنگو ردیف را از دیتابیس پاک می‌کند اما فایل واقعی روی
    media/ را دست‌نخورده رها می‌کند.

    این‌جا عمداً به‌جای بازنویسیِ ProductImage.delete()، به سیگنال
    post_delete وصل شده‌ایم: وقتی خودِ محصول (Product) حذف می‌شود، جنگو
    برای پاک‌کردنِ ردیف‌های وابسته‌ی آن (CASCADE) از یک مسیر بهینه‌ی
    داخلی (حذفِ SQL خام روی کل مجموعه) استفاده می‌کند که هرگز متد
    delete() هیچ مدلی را صدا نمی‌زند — پس اگر این منطق را روی
    ProductImage.delete() می‌نوشتیم، دقیقاً همان لحظه‌ای که بیشتر از همه
    لازم بود (حذف کل محصول) کار نمی‌کرد. اما همین که *هر* گیرنده‌ای به
    pre_delete/post_delete این مدل وصل باشد، جنگو به‌طور خودکار از آن
    مسیر بهینه صرف‌نظر می‌کند و هر ردیف را جداگانه پردازش می‌کند — یعنی
    post_delete برای هر ProductImage، چه حذف مستقیم چه از طریق CASCADE،
    قطعاً اجرا می‌شود.

    مثل save() بالا، حذف واقعی فایل با transaction.on_commit به تأخیر
    می‌افتد تا اگر تراکنش حذف rollback شد، فایل هنوز روی دیسک باشد.
    """
    if not instance.image:
        return
    storage, name = instance.image.storage, instance.image.name
    transaction.on_commit(lambda: storage.delete(name))


class ProductVariant(models.Model):
    """A purchasable flavor + weight/serving combination of a product,
    each with its own price and stock (e.g. 'شکلات دبل، 2270 گرم').

    "label" is the exact text shown on the weight/serving selector button
    in the UI (e.g. "2270 گرم (74 سروینگ)"); weight_grams/servings_count
    are kept as separate numeric fields too so we can sort/filter variants
    later without parsing that text.
    """

    product = models.ForeignKey(Product, verbose_name="محصول", related_name="variants", on_delete=models.CASCADE)
    flavor = models.ForeignKey(
        Flavor,
        verbose_name="طعم",
        related_name="variants",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        help_text="برای محصولاتی مثل کپسول که طعم ندارند خالی بگذارید",
    )
    label = models.CharField("برچسب وزن/سروینگ", max_length=100, help_text="مثال: ۲۲۷۰ گرم (۷۴ سروینگ)")
    weight_grams = models.PositiveIntegerField("وزن (گرم)", null=True, blank=True)
    servings_count = models.PositiveIntegerField("تعداد سروینگ", null=True, blank=True)
    sku = models.CharField("کد کالا (SKU)", max_length=50, unique=True, blank=True, null=True)
    price = models.PositiveIntegerField("قیمت (تومان)")
    compare_at_price = models.PositiveIntegerField(
        "قیمت قبل از تخفیف (تومان)", null=True, blank=True, help_text="خالی بگذارید اگر تخفیف ندارد"
    )
    stock = models.PositiveIntegerField("موجودی", default=0)
    is_active = models.BooleanField("فعال", default=True)

    class Meta:
        verbose_name = "تنوع محصول (Variant)"
        verbose_name_plural = "تنوع‌های محصول (Variants)"
        ordering = ["price"]

    def __str__(self):
        flavor_part = f"{self.flavor} - " if self.flavor else ""
        return f"{self.product.name} ({flavor_part}{self.label})"

    @property
    def is_in_stock(self):
        return self.is_active and self.stock > 0

    @property
    def discount_percent(self):
        if self.compare_at_price and self.compare_at_price > self.price:
            return round((self.compare_at_price - self.price) * 100 / self.compare_at_price)
        return 0


class ProductSpec(models.Model):
    """A single key/value technical spec row shown in the product's
    'مشخصات فنی' tab (e.g. key='وزن بسته‌بندی', value='2270 گرم').

    Deliberately free-form (per-product key/value pairs) rather than a
    category-level attribute-definition table — different product
    categories can show completely different sets of specs without any
    schema change. If we later need cross-product spec filtering (e.g.
    "show all products with protein >= 20g"), that's the point to
    introduce a proper AttributeDefinition model; not needed yet.
    """

    product = models.ForeignKey(Product, verbose_name="محصول", related_name="specs", on_delete=models.CASCADE)
    key = models.CharField("عنوان مشخصه", max_length=100)
    value = models.CharField("مقدار", max_length=200)
    order = models.PositiveIntegerField("ترتیب نمایش", default=0)

    class Meta:
        verbose_name = "مشخصه فنی"
        verbose_name_plural = "مشخصات فنی"
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.product.name} - {self.key}"