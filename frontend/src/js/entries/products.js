import { addToCart } from "../cartDrawer.js";
import { showToast } from "../toast.js";

let currentModalProduct = null;

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
