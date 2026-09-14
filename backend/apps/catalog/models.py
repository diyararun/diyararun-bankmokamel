import io
import os

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import models
from django_jalali.db import models as jmodels
from PIL import Image, ImageOps

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
        help_text="حداکثر ۸ دسته‌بندی محبوب در صفحه‌ی اصلی نمایش داده می‌شود؛ فقط برای دسته‌بندی‌های اصلی قابل انتخاب است.",
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
# enough that the resulting JPEG stays tiny (a few hundred KB at most,
# usually well under 100KB — see the docstring on save() for why this
# matters for page speed, not just layout consistency).
PRODUCT_IMAGE_CANVAS_SIZE = 1000
PRODUCT_IMAGE_JPEG_QUALITY = 85


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

    def save(self, *args, **kwargs):
        # `_committed` is False exactly when a NEW file was just assigned
        # to this field (an upload happening right now) — as opposed to
        # re-saving an existing row without touching the image (e.g.
        # editing alt_text). Without this check, every admin save would
        # re-process (and re-compress) an already-normalized image.
        if self.image and not self.image._committed:
            self.image = self.normalize_image(self.image)
        super().save(*args, **kwargs)

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

        image.thumbnail((PRODUCT_IMAGE_CANVAS_SIZE, PRODUCT_IMAGE_CANVAS_SIZE), Image.LANCZOS)

        canvas = Image.new("RGB", (PRODUCT_IMAGE_CANVAS_SIZE, PRODUCT_IMAGE_CANVAS_SIZE), (255, 255, 255))
        offset = (
            (PRODUCT_IMAGE_CANVAS_SIZE - image.width) // 2,
            (PRODUCT_IMAGE_CANVAS_SIZE - image.height) // 2,
        )
        canvas.paste(image, offset)

        buffer = io.BytesIO()
        canvas.save(buffer, format="JPEG", quality=PRODUCT_IMAGE_JPEG_QUALITY, optimize=True)

        original_name = os.path.splitext(os.path.basename(uploaded_file.name))[0]
        return ContentFile(buffer.getvalue(), name=f"{original_name}.jpg")


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
    sku = models.CharField("کد کالا (SKU)", max_length=50, unique=True)
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