from django.contrib import admin

from .models import Review


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
