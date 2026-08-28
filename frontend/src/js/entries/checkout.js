import { showToast } from "../toast.js";

// TODO: وقتی سبد خرید واقعی به بک‌اند وصل شد، این آیتم‌های نمونه باید از
// یک context جنگو (مثلاً request.session["cart"] یا مدل Order) خوانده شوند.
const checkoutItems = [
  { name: "وی گلد استاندارد 100%", price: 3570000, emoji: "", quantity: 1 },
  {
    name: "کراتین میکرونایز شده ۳۰۰ گرم",
    price: 1150000,
    emoji: "",
    quantity: 1,
  },
];

let selectedDeliveryDate = "";

function renderCheckoutSummary() {
  const list = document.getElementById("checkoutItemsList");
  if (!list) return;
  list.innerHTML = "";

  checkoutItems.forEach((item) => {
    const div = document.createElement("div");
    div.className =
      "flex items-center justify-between p-2.5 bg-slate-50 border border-slate-100 rounded-2xl";
    div.innerHTML = `
      <div class="flex items-center gap-2.5">
        <div class="w-9 h-9 bg-white rounded-xl flex items-center justify-center text-lg shadow-sm shrink-0">${item.emoji}</div>
        <div>
          <h4 class="font-bold text-xs text-slate-900 line-clamp-1">${item.name}</h4>
          <span class="text-[10px] text-slate-400">${item.quantity} عدد</span>
        </div>
      </div>
      <span class="text-xs font-bold text-slate-800">${(item.price * item.quantity).toLocaleString()} تومان</span>
    `;
    list.appendChild(div);
  });
}

function buildDeliveryCalendar() {
  const container = document.getElementById("deliveryCalendar");
  if (!container) return;
  container.innerHTML = "";

  // تاریخ‌های نمونه ۶ روز کاری متوالی
  const days = [
    { dayName: "امروز", dateNum: "۲۳", month: "مرداد" },
    { dayName: "فردا", dateNum: "۲۴", month: "مرداد" },
    { dayName: "شنبه", dateNum: "۲۵", month: "مرداد" },
    { dayName: "یکشنبه", dateNum: "۲۶", month: "مرداد" },
    { dayName: "دوشنبه", dateNum: "۲۷", month: "مرداد" },
    { dayName: "سه‌شنبه", dateNum: "۲۸", month: "مرداد" },
  ];

  days.forEach((day, index) => {
    const btn = document.createElement("button");
    btn.type = "button";
    const isSelected = index === 0;

    btn.className = `p-3 rounded-2xl border text-center transition-all flex flex-col items-center justify-center gap-1 ${
      isSelected
        ? "border-2 border-red-600 bg-red-50 text-red-600 font-bold shadow-sm"
        : "border-slate-200 bg-slate-50/50 hover:border-slate-300 text-slate-700"
    }`;

    btn.innerHTML = `
      <span class="text-[10px] opacity-75">${day.dayName}</span>
      <span class="text-sm font-black">${day.dateNum} ${day.month}</span>
    `;

    btn.onclick = () => {
      document.querySelectorAll("#deliveryCalendar button").forEach((b) => {
        b.className =
          "p-3 rounded-2xl border text-center transition-all flex flex-col items-center justify-center gap-1 border-slate-200 bg-slate-50/50 hover:border-slate-300 text-slate-700";
      });
      btn.className =
        "p-3 rounded-2xl border-2 border-red-600 bg-red-50 text-red-600 font-bold shadow-sm text-center flex flex-col items-center justify-center gap-1";
      selectedDeliveryDate = `${day.dayName} (${day.dateNum} ${day.month})`;
      document.getElementById("selectedDateBadge").innerText =
        selectedDeliveryDate;
      showToast(
        "تاریخ ارسال انتخاب شد",
        `تحویل برای روز ${selectedDeliveryDate} تنظیم شد.`,
      );
    };

    container.appendChild(btn);
  });

  selectedDeliveryDate = "امروز (۲۳ مرداد)";
}

function applyCoupon() {
  const code = document.getElementById("couponCode").value.trim();
  if (code) {
    showToast(
      "کد تخفیف اعمال شد",
      `کد «${code}» با موفقیت ثبت گردید (۱۰٪ تخفیف اضافه).`,
    );
  } else {
    showToast("خطا", "لطفاً کد تخفیف را وارد کنید.");
  }
}

function handleFinalSubmit(event) {
  event.preventDefault();
  showToast("در حال انتقال...", "سفارش شما ثبت شد. انتقال به درگاه پرداخت...");
  // TODO: اتصال به view واقعی جنگو برای ثبت سفارش (مدل Order) و اتصال به درگاه بانکی
  setTimeout(() => {
    alert("سفارش شما با موفقیت ثبت شد! شماره پیگیری: BM-98241");
  }, 1500);
}

window.applyCoupon = applyCoupon;
window.handleFinalSubmit = handleFinalSubmit;

document.addEventListener("DOMContentLoaded", () => {
  renderCheckoutSummary();
  buildDeliveryCalendar();
});
