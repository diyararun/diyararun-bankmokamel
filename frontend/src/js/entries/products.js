import { addToCart } from "../cartDrawer.js";
import { showToast } from "../toast.js";

let currentModalProduct = null;

function openQuickView(title, price, emoji, category, brand, desc) {
  currentModalProduct = { name: title, price: price, emoji: emoji };
  document.getElementById("modalTitle").innerText = title;
  document.getElementById("modalPrice").innerText = price.toLocaleString();
  document.getElementById("modalEmoji").innerText = emoji;
  document.getElementById("modalCategory").innerText = category;
  document.getElementById("modalBrand").innerText = brand;
  document.getElementById("modalDesc").innerText = desc;

  const modal = document.getElementById("quickViewModal");
  const content = modal.querySelector("> div:nth-child(2)");

  modal.classList.remove("opacity-0", "pointer-events-none");
  modal.classList.add("opacity-100");
  content.classList.remove("scale-95");
  content.classList.add("scale-100");
}

function closeQuickView() {
  const modal = document.getElementById("quickViewModal");
  const content = modal.querySelector("> div:nth-child(2)");

  content.classList.remove("scale-100");
  content.classList.add("scale-95");
  modal.classList.remove("opacity-100");
  modal.classList.add("opacity-0", "pointer-events-none");
}

window.openQuickView = openQuickView;
window.closeQuickView = closeQuickView;

function initFilters() {
  const priceRange = document.getElementById("priceRange");
  const priceRangeValue = document.getElementById("priceRangeValue");
  if (priceRange && priceRangeValue) {
    priceRange.addEventListener("input", (e) => {
      priceRangeValue.innerText = `تا ${Number(e.target.value).toLocaleString()} تومان`;
    });
  }

  const filterCheckboxes = document.querySelectorAll(".filter-checkbox");
  const activeFilterCountEl = document.getElementById("activeFilterCount");

  function updateActiveFilterCount() {
    if (!activeFilterCountEl) return;
    const count = document.querySelectorAll(".filter-checkbox:checked").length;
    activeFilterCountEl.innerText = count.toLocaleString("fa-IR");
    if (count > 0) {
      activeFilterCountEl.classList.remove("hidden");
      activeFilterCountEl.classList.add("inline-flex");
    } else {
      activeFilterCountEl.classList.add("hidden");
      activeFilterCountEl.classList.remove("inline-flex");
    }
  }

  filterCheckboxes.forEach((cb) =>
    cb.addEventListener("change", updateActiveFilterCount),
  );
  updateActiveFilterCount();

  // Weight-range radios: give them the same instant, JS-driven highlight
  // that flavor/weight selection has on the product-detail page — no
  // waiting for "اعمال فیلترها" + a page reload to see which one is
  // active. Native <input type="radio"> already handles the actual
  // checked/unchecked state and keyboard access; this just keeps each
  // <label>'s Tailwind classes in sync with it on every change.
  const weightRadios = document.querySelectorAll('input[name="weight_range"]');
  if (weightRadios.length > 0) {
    const applyWeightStyles = () => {
      weightRadios.forEach((radio) => {
        const label = radio.closest("label");
        if (!label) return;
        label.className = `p-2 border ${
          radio.checked
            ? "border-red-600 bg-red-50 text-red-600 font-bold"
            : "border-slate-200 hover:border-red-300 hover:bg-red-50/40 hover:text-red-600 text-slate-700 font-medium transition-colors"
        } rounded-xl text-center cursor-pointer`;
      });
    };

    // A fresh visit (no ?weight_range= in the URL yet) shouldn't leave
    // every option looking unselected — default to the first one, same
    // as product-detail always having a real default variant selected.
    const alreadyChecked = Array.from(weightRadios).some((r) => r.checked);
    if (!alreadyChecked) weightRadios[0].checked = true;

    weightRadios.forEach((radio) =>
      radio.addEventListener("change", applyWeightStyles),
    );
    applyWeightStyles();
  }

  window.resetFilters = function resetFilters() {
    if (priceRange) {
      priceRange.value = 4500000;
      priceRangeValue.innerText = "تا ۴,۵۰۰,۰۰۰ تومان";
    }

    filterCheckboxes.forEach((cb) => {
      cb.checked = cb.defaultChecked;
    });
    const availabilityToggle = document.getElementById("availabilityToggle");
    if (availabilityToggle) {
      availabilityToggle.checked = availabilityToggle.defaultChecked;
    }
    updateActiveFilterCount();

    showToast("بازنشانی فیلترها", "تمام فیلترها به حالت اولیه برگشتند.");
  };
}

document.addEventListener("DOMContentLoaded", () => {
  initFilters();
  document.getElementById("modalAddBtn")?.addEventListener("click", () => {
    if (currentModalProduct) {
      addToCart(
        currentModalProduct.name,
        currentModalProduct.price,
        currentModalProduct.emoji,
      );
    }
    closeQuickView();
  });
});