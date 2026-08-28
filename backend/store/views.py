from django.shortcuts import render


def index(request):
    return render(request, "pages/index.html", {"active_nav": "home"})


def products(request):
    return render(request, "pages/products.html", {"active_nav": "products"})


def product_detail(request, slug=None):
    return render(
        request,
        "pages/product_detail.html",
        {"slug": slug, "active_nav": "products"},
    )


def about(request):
    return render(request, "pages/about.html", {"active_nav": "about"})


def contact(request):
    return render(request, "pages/contact.html", {"active_nav": "contact"})


def checkout(request):
    return render(request, "pages/checkout.html", {"active_nav": "checkout"})
