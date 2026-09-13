from django.db.models import Prefetch

from apps.cart.services import get_cart
from apps.catalog.models import Category

from .models import SiteSettings


def cart(request):
    """Makes the cart badge count available on every page (server-rendered
    on first load), so the badge shows the real persisted count
    immediately instead of starting at 0 until cartDrawer.js runs.

    Uses create=False — a page view alone should never create an empty
    Cart row for a visitor who hasn't added anything yet.
    """
    current_cart = get_cart(request, create=False)
    total_quantity = current_cart.total_quantity if current_cart else 0
    return {"cart_total_quantity": total_quantity}


def site_settings(request):
    """Makes the editable site-wide content (hero copy, footer/contact
    info, social links, about-page text) available on every page as
    {{ site_settings.* }}, so header/footer partials and any page can use
    it without each view fetching it manually.
    """
    return {"site_settings": SiteSettings.load()}


def category_drawer(request):
    """Feeds the "همه دسته‌بندی‌ها" drawer (partials/category_drawer.html,
    included from base.html on every page) with real data instead of the
    handful of hardcoded example categories it used to have.

    Only top-level categories are queried directly; each one's active
    subcategories are attached as `.active_children` via Prefetch so the
    template can loop over them without a second query per category
    (Category.parent/children already existed on the model — this is the
    first place that actually uses it). Subcategories intentionally carry
    no image here — only the parent category's `icon` is shown, per how
    this section was scoped.
    """
    top_level_categories = (
        Category.objects.filter(is_active=True, parent__isnull=True)
        .prefetch_related(
            Prefetch(
                "children",
                queryset=Category.objects.filter(is_active=True).order_by("name"),
                to_attr="active_children",
            )
        )
        .order_by("name")
    )
    return {"drawer_categories": top_level_categories}