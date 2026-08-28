import { showToast } from "./toast.js";

// مدیریت حالت سبد خرید (سمت کلاینت)
// توجه: در حال حاضر سبد خرید فقط در حافظه‌ی مرورگر نگه‌داری می‌شود و با
// رفتن به صفحه‌ی دیگر خالی می‌شود (رفتار اصلی پروژه‌ی اولیه حفظ شده است).
// برای پایدارسازی سبد خرید بین صفحات/رفرش، این ماژول باید به یک API جنگو
// (مثلاً /api/cart/) یا localStorage وصل شود.
let cart = [];

export function addToCart(name, price, emoji) {
  const existingItem = cart.find((item) => item.name === name);
  if (existingItem) {
    existingItem.quantity += 1;
  } else {
    cart.push({ name, price, emoji, quantity: 1 });
  }

  updateCartUI();
  showToast("افزوده شد به سبد خرید", `«${name}» با موفقیت به سبد اضافه شد.`);
}

// افزودن چند عدد از یک محصول در یک عملیات، بدون نمایش Toast تکراری
// (برای صفحه‌ی جزئیات محصول که خودش پیام تجمیعی نمایش می‌دهد)
export function addMultipleToCart(name, price, emoji, quantity) {
  const existingItem = cart.find((item) => item.name === name);
  if (existingItem) {
    existingItem.quantity += quantity;
  } else {
    cart.push({ name, price, emoji, quantity });
  }
  updateCartUI();
}

export function updateQuantity(name, delta) {
  const item = cart.find((i) => i.name === name);
  if (item) {
    item.quantity += delta;
    if (item.quantity <= 0) {
      cart = cart.filter((i) => i.name !== name);
    }
  }
  updateCartUI();
}

export function updateCartUI() {
  const badge = document.getElementById("cartBadge");
  if (!badge) return;

  const totalCount = cart.reduce((sum, item) => sum + item.quantity, 0);
  badge.innerText = totalCount;

  badge.classList.add("animate-bounce-short");
  setTimeout(() => badge.classList.remove("animate-bounce-short"), 300);

  renderCartDrawer();
}

export function renderCartDrawer() {
  const cartContent = document.getElementById("cartContent");
  const cartFooter = document.getElementById("cartFooter");
  if (!cartContent || !cartFooter) return;

  if (cart.length === 0) {
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
  let totalPrice = 0;

  cart.forEach((item) => {
    const itemTotal = item.price * item.quantity;
    totalPrice += itemTotal;
    itemsHtml += `
      <div class="flex items-center justify-between p-3.5 bg-slate-50 border border-slate-100 rounded-2xl">
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 bg-white rounded-xl flex items-center justify-center text-2xl shadow-sm shrink-0">
            ${item.emoji}
          </div>
          <div>
            <h4 class="font-bold text-xs text-slate-900 line-clamp-1">${item.name}</h4>
            <span class="text-[11px] text-red-600 font-bold mt-1 block">${item.price.toLocaleString()} تومان</span>
          </div>
        </div>
        <div class="flex items-center gap-2 bg-white border border-slate-200 rounded-lg px-2 py-1">
          <button onclick="updateQuantity('${item.name}', 1)" class="text-slate-600 hover:text-red-600 font-bold text-sm">+</button>
          <span class="text-xs font-bold text-slate-800 w-4 text-center">${item.quantity}</span>
          <button onclick="updateQuantity('${item.name}', -1)" class="text-slate-600 hover:text-red-600 font-bold text-sm">-</button>
        </div>
      </div>
    `;
  });

  itemsHtml += "</div>";
  cartContent.innerHTML = itemsHtml;
  document.getElementById("cartTotalPrice").innerText =
    `${totalPrice.toLocaleString()} تومان`;
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

// در دسترس بودن سراسری برای onclick های داخل HTML
window.addToCart = addToCart;
window.updateQuantity = updateQuantity;
window.openCartDrawer = openCartDrawer;
window.closeCartDrawer = closeCartDrawer;
