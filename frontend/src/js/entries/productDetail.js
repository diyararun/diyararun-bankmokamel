import "../../css/product-detail.css";

import { addToCart } from "../cartDrawer.js";

let currentQuantity = 1;

// Real product data, injected by Django via {{ product_json|json_script:"product-data" }}
// in product_detail.html (see apps/catalog/views.py ProductDetailView).
const productData = JSON.parse(
  document.getElementById("product-data").textContent,
);

// The weight/serving variant currently selected for "افزودن به سبد خرید" —
// starts at the server-rendered default, changes when the customer clicks
// a different weight pill (see selectVariant() below).
let selectedVariantId = productData.defaultVariantId;

const productImageHTML = (url) =>
  `<img class="w-full h-full object-cover" src="${url}" alt="${productData.name}" />`;

// Falls back to a single empty placeholder if the product has no
// uploaded images yet, so the gallery/thumbnail code below never has to
// special-case an empty array.
const galleryImages =
  productData.images.length > 0
    ? productData.images.map(productImageHTML)
    : [productImageHTML("")];
let currentGalleryIndex = 0;

// این آرایه به‌جای «cart» عمومی (که حالا در cartDrawer.js مدیریت می‌شود) فقط
// برای شمارش تعداد همین محصول در حال افزودن استفاده می‌شود.
function renderThumbnails() {
  const container = document.getElementById("thumbnailsContainer");
  if (!container) return;
  container.innerHTML = "";

  const maxVisible = 4;
  const total = galleryImages.length;

  for (let i = 0; i < Math.min(total, maxVisible); i++) {
    const isLastAndHasMore = i === maxVisible - 1 && total > maxVisible;
    const button = document.createElement("button");

    if (isLastAndHasMore) {
      const remaining = total - maxVisible + 1;
      button.className =
        "thumb-btn h-16 bg-slate-100 rounded-xl border border-slate-200 flex items-center justify-center relative overflow-hidden group backdrop-blur-sm";
      button.innerHTML = `
        <div class="w-full h-full opacity-40 blur-[1px] select-none">${galleryImages[i]}</div>
        <div class="absolute inset-0 bg-slate-900/60 flex flex-col items-center justify-center text-white font-black text-xs group-hover:bg-red-600/80 transition-colors">
          <span>...</span>
          <span class="text-[10px] font-medium">+${remaining} عکس</span>
        </div>
      `;
      button.onclick = () => {
        currentGalleryIndex = i;
        openGalleryModal();
      };
    } else {
      const isSelected = i === currentGalleryIndex;
      button.className = `thumb-btn h-16 bg-slate-50 rounded-xl flex items-center justify-center overflow-hidden transition-all ${
        isSelected
          ? "border-2 border-red-600"
          : "border border-slate-200 hover:border-slate-300"
      }`;
      button.innerHTML = galleryImages[i];
      button.onclick = () => selectImage(i);
    }

    container.appendChild(button);
  }
}

function selectImage(index) {
  currentGalleryIndex = index;
  document.getElementById("mainImageEmoji").innerHTML = galleryImages[index];
  renderThumbnails();
}

function openGalleryModal() {
  updateGalleryModalContent();
  const modal = document.getElementById("galleryModal");
  modal.classList.remove("opacity-0", "pointer-events-none");
  modal.classList.add("opacity-100");
}

function closeGalleryModal() {
  const modal = document.getElementById("galleryModal");
  modal.classList.remove("opacity-100");
  modal.classList.add("opacity-0", "pointer-events-none");
}

function changeGalleryImageWithAnimation(nextIndex) {
  const container = document.getElementById("modalEmojiContainer");
  container.classList.add("modal-img-hidden");

  setTimeout(() => {
    currentGalleryIndex = nextIndex;
    selectImage(currentGalleryIndex);
    updateGalleryModalContent();
    container.classList.remove("modal-img-hidden");
  }, 200);
}

function nextGalleryImage() {
  const nextIndex = (currentGalleryIndex + 1) % galleryImages.length;
  changeGalleryImageWithAnimation(nextIndex);
}

function prevGalleryImage() {
  const prevIndex =
    (currentGalleryIndex - 1 + galleryImages.length) % galleryImages.length;
  changeGalleryImageWithAnimation(prevIndex);
}

function updateGalleryModalContent() {
  document.getElementById("modalEmojiContainer").innerHTML =
    galleryImages[currentGalleryIndex];
  document.getElementById("modalImageCaption").innerText =
    `تصویر ${currentGalleryIndex + 1} از ${galleryImages.length} - ${productData.name}`;
}

function switchTab(tabKey) {
  const contents = document.querySelectorAll(".tab-content");
  contents.forEach((el) => el.classList.remove("active"));

  document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.classList.remove("text-red-600", "border-red-600");
    btn.classList.add("text-slate-500", "border-transparent");
  });

  const activeContent = document.getElementById(`tabContent-${tabKey}`);
  activeContent.classList.add("active");

  const activeBtn = document.getElementById(`tabBtn-${tabKey}`);
  activeBtn.classList.remove("text-slate-500", "border-transparent");
  activeBtn.classList.add("text-red-600", "border-red-600");
}

function adjustQuantity(delta) {
  currentQuantity += delta;
  if (currentQuantity < 1) currentQuantity = 1;
  document.getElementById("detailQuantity").innerText = currentQuantity;
}

// Switches the selected weight/serving variant: updates the price/compare
// price shown, which variant "افزودن به سبد خرید" will actually add, its
// disabled/"ناموجود" state, and the pill buttons' active styling.
function selectVariant(variantId) {
  const variant = productData.variants.find((v) => v.id === variantId);
  if (!variant) return;
  selectedVariantId = variant.id;

  document.getElementById("productPrice").innerText = variant.price;
  const compareEl = document.getElementById("productComparePrice");
  if (variant.compareAtPrice) {
    compareEl.innerText = variant.compareAtPrice;
    compareEl.classList.remove("hidden");
  } else {
    compareEl.classList.add("hidden");
  }

  document.querySelectorAll(".js-variant-option").forEach((btn) => {
    const isSelected = Number(btn.dataset.variantId) === variant.id;
    // Rebuilding className wholesale would silently undo the "hidden"
    // class selectFlavor() just set on buttons that don't match the
    // chosen flavor — carry it forward instead of wiping it.
    const wasHidden = btn.classList.contains("hidden");
    btn.className = `js-variant-option px-3 py-1.5 border-2 ${
      isSelected
        ? "border-red-600 text-red-600 font-bold bg-red-50"
        : "border-slate-200 text-slate-600 hover:border-red-300 hover:text-red-600"
    } rounded-lg text-xs transition-colors${wasHidden ? " hidden" : ""}`;
  });

  const addBtn = document.getElementById("mainAddToCartBtn");
  addBtn.dataset.variantId = variant.id;
  addBtn.disabled = !variant.inStock;
  document.getElementById("mainAddToCartLabel").innerText = variant.inStock
    ? "افزودن به سبد خرید"
    : "ناموجود";
}

// Selecting a flavor doesn't buy anything by itself — a flavor is one half
// of which ProductVariant actually gets added to the cart, the weight/
// serving pill is the other half. So this: (1) highlights the chosen
// flavor pill, (2) shows only the weight pills that exist for THAT flavor
// (a variant's flavorId either matches or it doesn't — hiding the rest
// stops the customer from picking a weight/flavor combination that was
// never a real product variant), and (3) auto-selects the first in-stock
// variant among what's left, via selectVariant() above.
function selectFlavor(flavorId) {
  document.querySelectorAll(".js-flavor-option").forEach((btn) => {
    const isSelected = Number(btn.dataset.flavorId) === flavorId;
    btn.className = `js-flavor-option px-3 py-1.5 border-2 ${
      isSelected
        ? "border-red-600 text-red-600 font-bold bg-red-50"
        : "border-slate-200 text-slate-600 hover:border-red-300 hover:text-red-600"
    } rounded-lg text-xs transition-colors`;
  });

  let firstMatch = null;
  let firstInStockMatch = null;
  document.querySelectorAll(".js-variant-option").forEach((btn) => {
    const variant = productData.variants.find(
      (v) => v.id === Number(btn.dataset.variantId),
    );
    const matches = !!variant && variant.flavorId === flavorId;
    btn.classList.toggle("hidden", !matches);
    if (matches) {
      firstMatch = firstMatch || variant;
      if (variant.inStock) firstInStockMatch = firstInStockMatch || variant;
    }
  });

  const target = firstInStockMatch || firstMatch;
  if (target) selectVariant(target.id);
}

function addCurrentProductToCart() {
  addToCart(selectedVariantId, currentQuantity);
}

window.selectImage = selectImage;
window.openGalleryModal = openGalleryModal;
window.closeGalleryModal = closeGalleryModal;
window.nextGalleryImage = nextGalleryImage;
window.prevGalleryImage = prevGalleryImage;
window.switchTab = switchTab;
window.adjustQuantity = adjustQuantity;
window.addCurrentProductToCart = addCurrentProductToCart;

document.addEventListener("DOMContentLoaded", () => {
  renderThumbnails();

  document.querySelectorAll(".js-variant-option").forEach((btn) => {
    btn.addEventListener("click", () =>
      selectVariant(Number(btn.dataset.variantId)),
    );
  });

  const flavorButtons = document.querySelectorAll(".js-flavor-option");
  flavorButtons.forEach((btn) => {
    btn.addEventListener("click", () =>
      selectFlavor(Number(btn.dataset.flavorId)),
    );
  });
  // Apply the server-highlighted default flavor's filtering on load, so
  // the weight pills shown at first paint already match it instead of
  // listing every flavor's weights until the first click.
  if (flavorButtons.length > 0) {
    const defaultVariant = productData.variants.find(
      (v) => v.id === productData.defaultVariantId,
    );
    if (defaultVariant && defaultVariant.flavorId != null) {
      selectFlavor(defaultVariant.flavorId);
    }
  }

  const relatedSlider = document.getElementById("relatedSlider");
  if (relatedSlider) {
    document
      .getElementById("relatedNext")
      ?.addEventListener("click", () =>
        relatedSlider.scrollBy({ left: -280, behavior: "smooth" }),
      );
    document
      .getElementById("relatedPrev")
      ?.addEventListener("click", () =>
        relatedSlider.scrollBy({ left: 280, behavior: "smooth" }),
      );
  }
});