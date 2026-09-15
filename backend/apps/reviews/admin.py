from django.contrib import admin

# Patches Django admin so every plain number field (e.g. Review.rating,
# if a moderator ever edits it directly) accepts Persian/Arabic-indic
# digits — see the module docstring in apps/store/admin_persian_numbers.py.
import apps.store.admin_persian_numbers  # noqa: F401

# Adds the "keep native browser validation errors from popping up in
# English" and "don't wipe already-chosen files on a validation error"
# fixes to every ModelAdmin — see the module docstring in
# apps/store/admin_ux_fixes.py.
import apps.store.admin_ux_fixes  # noqa: F401
from apps.store.persian_numerals import format_jalali_datetime

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "rating", "is_approved", "is_verified_purchase", "created_at_display")
    list_filter = ("is_approved", "is_verified_purchase", "rating")
    search_fields = ("product__name", "user__phone", "comment")
    # Moderation workflow: staff approve reviews from this list view directly
    actions = ["approve_reviews"]

    @admin.display(description="تاریخ ثبت", ordering="created_at")
    def created_at_display(self, obj):
        return format_jalali_datetime(obj.created_at)

    @admin.action(description="تایید نظرات انتخاب‌شده")
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
