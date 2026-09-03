from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse

import django_jalali.admin  # noqa: F401  (Jalali widget for updated_at)

from .models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """Singleton-style admin: no "add" button once a row exists, no
    delete option, and the list page skips straight to editing the one
    row instead of showing a table with a single entry in it.
    """

    fieldsets = (
        ("هیرو صفحه‌ی اصلی", {"fields": ("hero_title", "hero_subtitle", "hero_description")}),
        ("معرفی فروشگاه", {"fields": ("site_description",)}),
        ("صفحه‌ی درباره ما", {"fields": ("about_page_content",)}),
        ("اطلاعات تماس", {"fields": ("address", "phone", "email", "working_hours")}),
        ("شبکه‌های اجتماعی", {"fields": ("instagram_url", "telegram_url", "whatsapp_url")}),
    )
    readonly_fields = ("updated_at",)

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = SiteSettings.load()
        return redirect(reverse("admin:store_sitesettings_change", args=[obj.pk]))