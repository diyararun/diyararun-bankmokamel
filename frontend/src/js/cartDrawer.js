import { showToast } from "./toast.js";
import { postForm } from "./csrf.js";

// مدیریت حالت سبد خرید — حالا واقعاً به بک‌اند (apps.cart) وصل است.
// این ماژول دیگر خودش منبع حقیقت نیست؛ فقط آخرین پاسخ سرور را کش می‌کند
// و بعد از هر تغییر، دوباره از سرور می‌خواند تا UI و دیتابیس هیچ‌وقت از
// هم عقب نیفتند.
let cart = { items: [], total_quantity: 0, total_price: 0 };

async function loadCartFromServer() {
  try {
    const response = await fetch("/cart/", {
      headers: { "X-Requested-With": "XMLHttpRequest" },
    });
    cart = await response.json();
  } catch (err) {
    console.error("بارگذاری سبد خرید ناموفق بود:", err);
  }
  renderCartUI();
}

export async function addToCart(variantId, quantity = 1) {
  try {
    cart = await postForm("/cart/add/", { variant_id: variantId, quantity });
  } catch (err) {
    console.error("افزودن به سبد خرید ناموفق بود:", err);
    showToast("خطا", "افزودن به سبد خرید ناموفق بود. دوباره تلاش کنید.");
    return;
  }
  renderCartUI();
  showToast("افزوده شد به سبد خرید", "محصول با موفقیت به سبد اضافه شد.");
}

export async function updateQuantity(variantId, delta) {
  try {
    cart = await postForm("/cart/update/", { variant_id: variantId, delta });
  } catch (err) {
    console.error("به‌روزرسانی سبد خرید ناموفق بود:", err);
    showToast("خطا", "به‌روزرسانی سبد خرید ناموفق بود.");
    return;
  }
  renderCartUI();
}

export async function removeFromCart(variantId) {
  try {
    cart = await postForm("/cart/remove/", { variant_id: variantId });
  } catch (err) {
    console.error("حذف از سبد خرید ناموفق بود:", err);
    return;
  }
  renderCartUI();
}

function renderCartUI() {
  const badge = document.getElementById("cartBadge");
  if (badge) {
    badge.innerText = cart.total_quantity;
    badge.classList.add("animate-bounce-short");
    setTimeout(() => badge.classList.remove("animate-bounce-short"), 300);
  }
  renderCartDrawer();
}

export function renderCartDrawer() {
  const cartContent = document.getElementById("cartContent");
  const cartFooter = document.getElementById("cartFooter");
  if (!cartContent || !cartFooter) return;

  if (cart.items.length === 0) {
    cartContent.innerHTML = `
      <div class="h-full flex flex-col items-center justify-center text-center my-auto py-12">
        <div class="w-20 h-20 bg-slate-100 text-slate-400 rounded-full flex items-center justify-center mb-4 text-3xl">
          🛒
        </div>
        <h4 class="font-bold text-slate-800 text-base">هنوز محصولی در سبد وجود ندارد</h4>
        <p class="text-xs text-slate-400 mt-2 max-w-xs leading-relaxed">
          می‌توانید از بخش محصولات مکمل مورد نظر خود را انتخاب کرده و به سبد اضافه کنید.
        </p>
        <button onclick="closeCartDrawer()" class="mt-6 bg-slate-900 text-white text-xs font-bold px-6 py-3 rounded-xl hover:bg-red-600 transition-colors">
          مشاهده فروشگاه
        </button>
      </div>
    `;
    cartFooter.classList.add("hidden");
    return;
  }

  let itemsHtml = '<div class="space-y-4">';

  cart.items.forEach((item) => {
    const thumb = item.image_url
      ? `<img src="${item.image_url}" alt="${item.product_name}" class="w-full h-full object-cover" />`
      : "";
    itemsHtml += `
      <div class="flex items-center justify-between p-3.5 bg-slate-50 border border-slate-100 rounded-2xl">
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 bg-white rounded-xl overflow-hidden shrink-0">
            ${thumb}
          </div>
          <div>
            <h4 class="font-bold text-xs text-slate-900 line-clamp-1">${item.product_name}</h4>
            ${item.variant_label ? `<span class="text-[10px] text-slate-400 block mt-0.5">${item.variant_label}</span>` : ""}
            <span class="text-[11px] text-red-600 font-bold mt-1 block">${item.price.toLocaleString()} تومان</span>
          </div>
        </div>
        <div class="flex items-center gap-2 bg-white border border-slate-200 rounded-lg px-2 py-1">
          <button onclick="updateQuantity(${item.variant_id}, 1)" class="text-slate-600 hover:text-red-600 font-bold text-sm">+</button>
          <span class="text-xs font-bold text-slate-800 w-4 text-center">${item.quantity}</span>
          <button onclick="updateQuantity(${item.variant_id}, -1)" class="text-slate-600 hover:text-red-600 font-bold text-sm">-</button>
        </div>
      </div>
    `;
  });

  itemsHtml += "</div>";
  cartContent.innerHTML = itemsHtml;
  document.getElementById("cartTotalPrice").innerText =
    `${cart.total_price.toLocaleString()} تومان`;
  cartFooter.classList.remove("hidden");
}

export function openCartDrawer() {
  renderCartDrawer();
  const modal = document.getElementById("cartDrawerModal");
  const drawer = document.getElementById("cartDrawer");
  if (!modal || !drawer) return;

  modal.classList.remove("opacity-0", "pointer-events-none");
  modal.classList.add("opacity-100");
  drawer.classList.remove("-translate-x-full");
  drawer.classList.add("translate-x-0");
}

export function closeCartDrawer() {
  const modal = document.getElementById("cartDrawerModal");
  const drawer = document.getElementById("cartDrawer");
  if (!modal || !drawer) return;

  drawer.classList.remove("translate-x-0");
  drawer.classList.add("-translate-x-full");
  modal.classList.remove("opacity-100");
  modal.classList.add("opacity-0", "pointer-events-none");
}

// در دسترس بودن سراسری برای onclick های داخل HTML (تولیدشده توسط جنگو)
window.addToCart = addToCart;
window.updateQuantity = updateQuantity;
window.removeFromCart = removeFromCart;
window.openCartDrawer = openCartDrawer;
window.closeCartDrawer = closeCartDrawer;

// هر دکمه‌ی «افزودن به سبد» ساده (کارت محصول در لیست/محصولات مرتبط) با
// کلاس مشترک js-add-to-cart علامت‌گذاری شده — به‌جای بستن onclick جدا
// روی هر کارت، یک شنونده‌ی واحد و سراسری (event delegation) همه‌شان را
// پوشش می‌دهد، even برای کارت‌هایی که بعداً/داینامیک اضافه شوند.
document.addEventListener("click", (event) => {
  const btn = event.target.closest(".js-add-to-cart");
  if (!btn || btn.disabled) return;
  addToCart(btn.dataset.variantId, 1);
});

document.addEventListener("DOMContentLoaded", loadCartFromServer);