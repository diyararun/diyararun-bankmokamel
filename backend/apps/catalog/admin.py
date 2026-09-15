from django.contrib import admin

# Importing this module patches Django admin's FORMFIELD_FOR_DBFIELD_DEFAULTS
# so jDateField/jDateTimeField automatically get a Jalali-aware widget in
# every ModelAdmin — no mixin class needed in this version of django-jalali.
import django_jalali.admin  # noqa: F401

# Same idea as the django_jalali.admin import above, but for plain
# number fields (price, weight, stock, ...) instead of Jalali dates —
# see the module docstring for why a seller typing Persian digits needs
# this. Importing it is enough; it patches Django admin's
# FORMFIELD_FOR_DBFIELD_DEFAULTS for every ModelAdmin in the project.
import apps.store.admin_persian_numbers  # noqa: F401

# Adds the "keep native browser validation errors from popping up in
# English" and "don't wipe already-chosen product images on a
# validation error" fixes to every ModelAdmin — see the module
# docstring in apps/store/admin_ux_fixes.py.
import apps.store.admin_ux_fixes  # noqa: F401
from apps.store.persian_numerals import format_jalali_datetime

from .models import Brand, Category, Flavor, Product, ProductImage, ProductSpec, ProductVariant


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "is_main_category", "is_popular", "is_active")
    list_filter = ("is_active", "is_main_category", "is_popular")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    # BooleanField + choices (بالای models.py) یعنی این دو فیلد به‌جای
    # چک‌باکس، به‌صورت رادیو («بله»/«خیر») نمایش داده می‌شوند — دقیقاً
    # همان چیزی که خواسته شده بود.
    radio_fields = {"is_main_category": admin.HORIZONTAL, "is_popular": admin.HORIZONTAL}


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Flavor)
class FlavorAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    # نشست ۳۷: حداکثر ۵ تصویر برای هر محصول. توجه: صرفاً max_num باعث
    # می‌شود ادمین فرم خالیِ بیشتری برای اضافه‌کردن نشان ندهد، اما به‌تنهایی
    # جلوی ارسال دستیِ فرم‌های بیشتر (مثلاً با دستکاری POST) را نمی‌گیرد —
    # validate_max=True لازم است تا این سقف واقعاً در اعتبارسنجی فرم‌ست
    # اعمال شود و اگر کسی بیشتر از ۵ ردیف بفرستد، خطای واقعی برگردد.
    max_num = 5
    validate_max = True


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ("flavor", "label", "weight_grams", "servings_count", "sku", "price", "compare_at_price", "stock", "is_active")


class ProductSpecInline(admin.TabularInline):
    model = ProductSpec
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "brand",
        "is_best_seller",
        "is_featured_deal",
        "is_active",
        "created_at_display",
    )
    # is_best_seller/is_featured_deal are editable right here, in the list —
    # not on each product's own edit page — on purpose: with a few hundred
    # products, the seller needs to search/filter this same list down to
    # the handful they mean, then tick a checkbox and hit one "ذخیره" for
    # the whole (already-filtered, already-paginated) page. No separate
    # picker screen, no per-product field to hunt for.
    list_editable = ("is_best_seller", "is_featured_deal")
    list_filter = ("is_active", "is_best_seller", "is_featured_deal", "category", "brand")
    search_fields = ("name", "short_description")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline, ProductVariantInline, ProductSpecInline]

    @admin.display(description="تاریخ ایجاد", ordering="created_at")
    def created_at_display(self, obj):
        return format_jalali_datetime(obj.created_at)