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
