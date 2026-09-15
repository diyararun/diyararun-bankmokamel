from django.core.management.base import BaseCommand

from apps.catalog.models import ProductImage


class Command(BaseCommand):
    """One-off backfill for photos uploaded BEFORE ProductImage.save() started
    normalizing every new upload to a fixed white-padded square (see the
    ProductImage docstring in apps/catalog/models.py, نشست ۲۱ in the
    progress log). New uploads don't need this — only images that already
    existed in the database when that change shipped.

    Safe to run more than once: an already-normalized image (already a
    PRODUCT_IMAGE_CANVAS_SIZE square JPEG) just gets re-normalized to the
    same result, at the cost of one wasted re-encode.
    """

    help = (
        "Re-processes every existing product image through the same "
        "normalization new uploads get automatically (resize/pad to a "
        "fixed white square, fix EXIF rotation, flatten transparency). "
        "Run this once after deploying the ProductImage normalization "
        "change, to fix photos that were uploaded before it existed."
    )

    def handle(self, *args, **options):
        queryset = ProductImage.objects.all()
        total = queryset.count()
        if total == 0:
            self.stdout.write("هیچ تصویر محصولی در دیتابیس نیست — کاری برای انجام نبود.")
            return

        for index, product_image in enumerate(queryset, start=1):
            with product_image.image.open("rb") as source_file:
                normalized_file = ProductImage.normalize_image(source_file)
            # save=False: we don't want a second, redundant model .save()
            # right after this — the explicit product_image.save() below
            # (which the normal ProductImage.save() no-ops on, since the
            # file is already committed at this point) covers it.
            product_image.image.save(normalized_file.name, normalized_file, save=False)
            product_image.save()
            self.stdout.write(f"[{index}/{total}] {product_image}")

        self.stdout.write(self.style.SUCCESS(f"تمام شد — {total} تصویر بازپردازش شد."))
