// دراپ‌داون آیکون پروفایل در هدر (ویژگی جدید: نمایش پروفایل به‌جای دکمه ورود)
export function initProfileMenu() {
  const btn = document.getElementById("profileMenuBtn");
  const dropdown = document.getElementById("profileMenuDropdown");
  if (!btn || !dropdown) return;

  document.addEventListener("click", (e) => {
    const wrapper = document.getElementById("profileMenuWrapper");
    if (!wrapper) return;
    if (!wrapper.contains(e.target)) {
      dropdown.classList.add("hidden");
    }
  });
}

export function toggleProfileMenu() {
  const dropdown = document.getElementById("profileMenuDropdown");
  if (!dropdown) return;
  dropdown.classList.toggle("hidden");
}

window.toggleProfileMenu = toggleProfileMenu;
