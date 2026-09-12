from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import FormView

from apps.catalog.models import Product

from .forms import ReviewForm
from .models import Review


class ReviewCreateView(LoginRequiredMixin, FormView):
    """Handles the review-submission form on the product detail page.

    Login is required — per the project decision, reviews are tied to a
    real account rather than a free-typed name/email, since
    "is_verified_purchase" only makes sense once we actually know who
    the reviewer is. Anonymous users are redirected to the login page
    (LOGIN_URL) and bounced back here afterwards.

    POST-only: this view never renders its own page, it only ever
    redirects back to the product detail page (with a message), so there
    is no template_name / GET handling to write.
    """

    form_class = ReviewForm
    http_method_names = ["post"]

    def dispatch(self, request, *args, **kwargs):
        self.product = get_object_or_404(Product, slug=kwargs["slug"], is_active=True)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # update_or_create so a user resubmitting their review updates the
        # existing row instead of hitting the (product, user) unique
        # constraint with an error — resubmitting reads naturally as
        # "editing my review".
        Review.objects.update_or_create(
            product=self.product,
            user=self.request.user,
            defaults={
                "rating": form.cleaned_data["rating"],
                "comment": form.cleaned_data["comment"],
                "is_approved": False,  # every (re-)submission goes back through moderation
            },
        )
        messages.success(self.request, "دیدگاه شما ثبت شد و پس از بررسی نمایش داده می‌شود.")
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, "لطفاً امتیاز و متن دیدگاه را کامل وارد کنید.")
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse("store:product_detail", kwargs={"slug": self.product.slug})