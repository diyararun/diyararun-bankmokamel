// ==================== منوی همبرگری موبایل ====================
export function toggleMobileMenu() {
  const btn = document.getElementById("mobileMenuBtn");
  const menu = document.getElementById("mobileMenu");
  const backdrop = document.getElementById("mobileMenuBackdrop");
  if (!btn || !menu || !backdrop) return;

  const bars = btn.querySelectorAll(".hamburger-bar");
  const isOpen = btn.getAttribute("aria-expanded") === "true";

  if (isOpen) {
    menu.classList.remove("max-h-[30rem]", "opacity-100");
    menu.classList.add("max-h-0", "opacity-0");
    backdrop.classList.remove("opacity-100");
    backdrop.classList.add("opacity-0", "pointer-events-none");
    bars[0].classList.remove("translate-y-[7px]", "rotate-45");
    bars[1].classList.remove("opacity-0");
    bars[2].classList.remove("-translate-y-[7px]", "-rotate-45");
    btn.setAttribute("aria-expanded", "false");
    document.body.classList.remove("overflow-hidden");
  } else {
    menu.classList.remove("max-h-0", "opacity-0");
    menu.classList.add("max-h-[30rem]", "opacity-100");
    backdrop.classList.remove("opacity-0", "pointer-events-none");
    backdrop.classList.add("opacity-100");
    bars[0].classList.add("translate-y-[7px]", "rotate-45");
    bars[1].classList.add("opacity-0");
    bars[2].classList.add("-translate-y-[7px]", "-rotate-45");
    btn.setAttribute("aria-expanded", "true");
    document.body.classList.add("overflow-hidden");
  }
}

// بستن خودکار منو در صورت بزرگ شدن صفحه به سایز دسکتاپ
window.addEventListener("resize", () => {
  const btn = document.getElementById("mobileMenuBtn");
  if (
    window.innerWidth >= 768 &&
    btn &&
    btn.getAttribute("aria-expanded") === "true"
  ) {
    toggleMobileMenu();
  }
});

window.toggleMobileMenu = toggleMobileMenu;
