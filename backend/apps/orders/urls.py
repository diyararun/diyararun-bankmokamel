from django.urls import path

from . import views

# No app_name here on purpose — same reasoning as apps/catalog/urls.py:
# this is include()-d from apps/store/urls.py, which owns the "store"
# namespace, so this route stays reversible as "store:checkout" (already
# used in several templates) without renaming anything.
urlpatterns = [
    path("", views.CheckoutView.as_view(), name="checkout"),
]