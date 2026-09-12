from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse

import django_jalali.admin  # noqa: F401  (Jalali widget for date fields)

from .models import ContactMessage, SiteSettings, Testimonial


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """Singleton-style admin: no "add" button once a row exists, no
    delete option, and the list page skips straight to editing the one
    row instead of showing a table with a single entry in it.
    """

    fieldsets = (
        (
            "هیرو صفحه‌ی اصلی",
            {"fields": ("hero_title", "hero_subtitle", "hero_description", "hero_product")},
        ),
        ("معرفی فروشگاه", {"fields": ("site_description",)}),
        (
            "صفحه‌ی درباره ما",
            {
                "fields": (
                    "about_hero_title",
                    "about_hero_description",
                    "about_page_content",
                    "stat1_number",
                    "stat1_label",
                    "stat2_number",
                    "stat2_label",
                    "stat3_number",
                    "stat3_label",
                    "stat4_number",
                    "stat4_label",
                )
            },
        ),
        ("صفحه‌ی تماس با ما", {"fields": ("contact_hero_title", "contact_hero_description")}),
        ("اطلاعات تماس", {"fields": ("address", "phones", "emails", "working_hours")}),
        ("شبکه‌های اجتماعی", {"fields": ("instagram_url", "telegram_url", "whatsapp_url")}),
    )
    readonly_fields = ("updated_at",)
    # Renders hero_product as a type-to-search box (AJAX-backed by
    # ProductAdmin.search_fields in apps/catalog/admin.py) instead of a
    # <select> with every product in it — the whole point of this field.
    autocomplete_fields = ("hero_product",)

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = SiteSettings.load()
        return redirect(reverse("admin:store_sitesettings_change", args=[obj.pk]))


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("name", "rating", "is_active", "order")
    list_filter = ("is_active", "rating")
    search_fields = ("name", "comment")
    list_editable = ("order", "is_active")


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "subject", "is_read", "created_at")
    list_filter = ("is_read", "subject", "created_at")
    search_fields = ("name", "phone", "email", "message")
    readonly_fields = ("name", "phone", "email", "subject", "message", "created_at")
    actions = ["mark_as_read"]

    @admin.action(description="علامت‌گذاری به‌عنوان خوانده‌شده")
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)