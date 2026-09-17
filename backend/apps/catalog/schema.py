"""Schema.org (JSON-LD) structured data for catalog pages — نشست ۵۲،
مرحله‌ی ۲ از گزارشِ سئوی نشستِ ۵۱.

Kept in its own module (instead of inline in views.py or the template)
because building this dict correctly needs a few decisions documented
once, in one place, rather than scattered as inline template logic:

- Prices go into the schema as Iranian Rial (the real ISO 4217 currency
  code, "IRR"), not Toman — even though the rest of the site, and the
  price the shopper actually sees, is in Toman. schema.org's
  priceCurrency is meant to be a genuine ISO 4217 code, and there is no
  such code for Toman (1 Toman = 10 Rial). Putting a Toman number next
  to "IRR" as-is would tell Google the product costs a tenth of its
  real price, so every price here is the Toman price × 10.
- A product with several weight/flavor variants at different prices is
  represented as a single AggregateOffer (lowPrice/highPrice/
  offerCount) instead of picking one variant's price as if it were the
  only offer — this is Google's own recommended shape for a product
  with variants.
- aggregateRating is only included when the product actually has at
  least one approved review. Google Search Console flags/ignores an
  AggregateRating with a zero reviewCount, so omitting the block
  entirely in that case is more correct than emitting a fake one.
"""

import json

from django.core.serializers.json import DjangoJSONEncoder
from django.urls import reverse

# The same three character replacements Django's own `json_script`
# template filter applies internally (see django.utils.html). We can't
# use that filter directly here: it hardcodes type="application/json"
# on the <script> tag it renders, but search engines only parse
# structured data out of type="application/ld+json".
_JSON_LD_ESCAPES = {
    ord(">"): "\\u003E",
    ord("<"): "\\u003C",
    ord("&"): "\\u0026",
}

TOMAN_TO_RIAL = 10


def _to_rial(toman_amount):
    return None if toman_amount is None else toman_amount * TOMAN_TO_RIAL


def build_product_json_ld(product, request, reviews_count):
    """Returns a Schema.org ``Product`` dict for ``product``, ready to be
    passed to :func:`json_ld_script` and dropped into a
    ``<script type="application/ld+json">`` tag on the product-detail page.

    ``reviews_count`` is passed in rather than recomputed here because
    the view already has the approved-reviews queryset in context for
    the reviews tab — no reason to query it a second time.
    """
    product_url = request.build_absolute_uri(
        reverse("store:product_detail", kwargs={"slug": product.slug})
    )

    data = {
        "@context": "https://schema.org/",
        "@type": "Product",
        "name": product.name,
        "url": product_url,
    }

    images = [request.build_absolute_uri(img.image.url) for img in product.images.all()]
    if images:
        data["image"] = images

    description = (product.short_description or product.description or "").strip()
    if description:
        data["description"] = description

    if product.brand_id:
        data["brand"] = {"@type": "Brand", "name": product.brand.name}

    default_variant = product.default_variant
    if default_variant:
        data["sku"] = default_variant.sku

    active_variants = list(product.active_variants)
    if active_variants:
        prices_rial = [_to_rial(v.price) for v in active_variants]
        data["offers"] = {
            "@type": "AggregateOffer",
            "url": product_url,
            "priceCurrency": "IRR",
            "lowPrice": min(prices_rial),
            "highPrice": max(prices_rial),
            "offerCount": len(active_variants),
            "availability": (
                "https://schema.org/InStock"
                if any(v.is_in_stock for v in active_variants)
                else "https://schema.org/OutOfStock"
            ),
        }

    if reviews_count > 0 and product.average_rating is not None:
        data["aggregateRating"] = {
            "@type": "AggregateRating",
            "ratingValue": round(product.average_rating, 1),
            "reviewCount": reviews_count,
        }

    return data


def json_ld_script(data):
    """Serializes ``data`` the same safe way Django's own ``json_script``
    filter does, so it can be embedded directly inside a
    ``<script type="application/ld+json">`` tag without risking a
    ``</script>`` (or similar) breaking out of the tag early.
    """
    return json.dumps(data, cls=DjangoJSONEncoder).translate(_JSON_LD_ESCAPES)
