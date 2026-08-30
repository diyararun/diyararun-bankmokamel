from django.urls import path

from . import views

app_name = "store"

urlpatterns = [
    path("", views.index, name="index"),
    path("products/", views.products, name="products"),
    path("products/<slug:slug>/", views.product_detail, name="product_detail"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("checkout/", views.checkout, name="checkout"),
]
