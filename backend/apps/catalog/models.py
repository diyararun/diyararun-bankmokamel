from django.db import models
from django_jalali.db import models as jmodels


class Category(models.Model):
    """Product category (e.g. 'پروتئین', 'کراتین'). Self-referential so
    subcategories can be introduced later without a schema change."""

    name = models.CharField("نام دسته‌بندی", max_length=100)
    slug = models.SlugField("اسلاگ", max_length=120, unique=True)
    parent = models.ForeignKey(
        "self",
        verbose_name="دسته‌بندی والد",
        null=True,
        blank=True,
        related_name="children",
        on_delete=models.SET_NULL,
    )
    is_active = models.BooleanField("فعال", default=True)

    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"
        ordering = ["name"]

    def __str__(self):
        return self.name


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
    is_active = models.BooleanField("فعال (قابل نمایش)", default=True)
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


class ProductImage(models.Model):
    """One image in a product's gallery. is_primary marks the image shown
    on product cards and as the default detail-page image."""

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