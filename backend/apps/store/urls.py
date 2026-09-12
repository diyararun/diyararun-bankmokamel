from django.urls import include, path

from . import views

app_name = "store"

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    # Product list/detail views now live in apps.catalog (that's their
    # domain); included here (without a namespace of its own) so they stay
    # reversible as "store:products" / "store:product_detail".
    path("products/", include("apps.catalog.urls")),
    path("about/", views.AboutView.as_view(), name="about"),
    path("contact/", views.ContactView.as_view(), name="contact"),
    # Checkout view now lives in apps.orders (that's its domain); included
    # here (without a namespace of its own) so it stays reversible as
    # "store:checkout".
    path("checkout/", include("apps.orders.urls")),
]