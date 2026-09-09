export function openCategoryDrawer() {
  const modal = document.getElementById("categoryDrawerModal");
  const drawer = document.getElementById("categoryDrawer");
  if (!modal || !drawer) return;

  modal.classList.remove("opacity-0", "pointer-events-none");
  modal.classList.add("opacity-100");
  drawer.classList.remove("translate-x-full");
  drawer.classList.add("translate-x-0");
}

export function closeCategoryDrawer() {
  const modal = document.getElementById("categoryDrawerModal");
  const drawer = document.getElementById("categoryDrawer");
  if (!modal || !drawer) return;

  drawer.classList.remove("translate-x-0");
  drawer.classList.add("translate-x-full");
  modal.classList.remove("opacity-100");
  modal.classList.add("opacity-0", "pointer-events-none");
}

export function toggleSubCategory(id) {
  const subMenu = document.getElementById(id);
  const arrow = document.getElementById(`arrow-${id}`);
  if (!subMenu) return;

  // بررسی باز یا بسته بودن بر اساس grid-rows
  const isOpen = subMenu.classList.contains("grid-rows-[1fr]");

  if (isOpen) {
    // بسته شدن نرم
    subMenu.classList.remove("grid-rows-[1fr]");
    subMenu.classList.add("grid-rows-[0fr]");
    if (arrow) arrow.classList.remove("rotate-180");
  } else {
    // باز شدن نرم
    subMenu.classList.remove("grid-rows-[0fr]");
    subMenu.classList.add("grid-rows-[1fr]");
    if (arrow) arrow.classList.add("rotate-180");
  }
}

// در دسترس قرار دادن توابع به‌صورت سراسری
window.openCategoryDrawer = openCategoryDrawer;
window.closeCategoryDrawer = closeCategoryDrawer;
window.toggleSubCategory = toggleSubCategory;