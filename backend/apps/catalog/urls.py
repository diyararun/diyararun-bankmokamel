from django.urls import path

from . import views

# No app_name here on purpose: this urls.py is include()-d directly into
# apps/store/urls.py, which owns the "store" namespace. That keeps these
# routes reversible as "store:products" / "store:product_detail" — exactly
# what every template already uses — instead of forcing every {% url %}
# tag across the templates to be renamed to "catalog:...".
urlpatterns = [
    path("", views.ProductListView.as_view(), name="products"),
    path("<slug:slug>/", views.ProductDetailView.as_view(), name="product_detail"),
]