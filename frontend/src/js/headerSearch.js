import { showToast } from "./toast.js";

// اینپوت سرچ بازشونده در هدر
export function initHeaderSearch() {
  const searchBtn = document.getElementById("searchBtn");
  const searchInput = document.getElementById("searchInput");
  if (!searchBtn || !searchInput) return;

  searchBtn.addEventListener("click", () => {
    if (searchInput.classList.contains("w-0")) {
      searchInput.classList.remove("w-0", "opacity-0");
      searchInput.classList.add("w-48", "sm:w-64", "opacity-100");
      searchInput.focus();
    } else {
      if (searchInput.value.trim() !== "") {
        showToast("جستجو", `در حال جستجو برای: ${searchInput.value}`);
      } else {
        searchInput.classList.remove("w-48", "sm:w-64", "opacity-100");
        searchInput.classList.add("w-0", "opacity-0");
      }
    }
  });
}
