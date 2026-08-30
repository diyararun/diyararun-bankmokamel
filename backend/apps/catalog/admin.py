from django.contrib import admin

# Importing this module patches Django admin's FORMFIELD_FOR_DBFIELD_DEFAULTS
# so jDateField/jDateTimeField automatically get a Jalali-aware widget in
# every ModelAdmin — no mixin class needed in this version of django-jalali.
import django_jalali.admin  # noqa: F401

from .models import Brand, Category, Flavor, Product, ProductImage, ProductSpec, ProductVariant, Review


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


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


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ("flavor", "label", "weight_grams", "servings_count", "sku", "price", "compare_at_price", "stock", "is_active")


class ProductSpecInline(admin.TabularInline):
    model = ProductSpec
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "brand", "is_active", "created_at")
    list_filter = ("is_active", "category", "brand")
    search_fields = ("name", "short_description")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline, ProductVariantInline, ProductSpecInline]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "rating", "is_approved", "is_verified_purchase", "created_at")
    list_filter = ("is_approved", "is_verified_purchase", "rating")
    search_fields = ("product__name", "user__phone", "comment")
    # Moderation workflow: staff approve reviews from this list view directly
    actions = ["approve_reviews"]

    @admin.action(description="تایید نظرات انتخاب‌شده")
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)