import { showToast } from "../toast.js";

// ======================== Validation for checkout form fields =========================

const fullName = document.getElementById("fullName");
const phone = document.getElementById("phone");
const email = document.getElementById("email");
const nationalCode = document.getElementById("nationalCode");
const address = document.getElementById("address");
const postalCode = document.getElementById("postalCode");
const buildingNumber = document.getElementById("buildingNumber");
const unit = document.getElementById("unit");
const province = document.getElementById("province");
const city = document.getElementById("city");


function onlyNumbers(event) {
  const allowedKeys = [
    "Backspace",
    "Delete",
    "ArrowLeft",
    "ArrowRight",
    "Tab",
    "Home",
    "End",
  ];

  if (
    !/^[0-9]$/.test(event.key) &&
    !allowedKeys.includes(event.key) &&
    !(event.ctrlKey || event.metaKey)
  ) {
    event.preventDefault();
  }
}

function onlyPersianLetters(event) {
  const allowedKeys = [
    "Backspace",
    "Delete",
    "ArrowLeft",
    "ArrowRight",
    "Tab",
    "Home",
    "End",
  ];

  if (
    !/^[آ-ی\s‌]$/.test(event.key) &&
    !allowedKeys.includes(event.key) &&
    !(event.ctrlKey || event.metaKey)
  ) {
    event.preventDefault();
  }
}

function validateNumberInput(event) {
  if (!/^\d*$/.test(event.target.value)) {
    event.target.value = event.target.value.replace(/\D/g, "");
  }
}

function validatePersianInput(event) {
  event.target.value = event.target.value.replace(/[^آ-ی\s‌]/g, "");
}

nationalCode.addEventListener("keydown", onlyNumbers);
phone.addEventListener("keydown", onlyNumbers);
postalCode.addEventListener("keydown", onlyNumbers);
nationalCode.addEventListener("input", validateNumberInput);
phone.addEventListener("input", validateNumberInput);
postalCode.addEventListener("input", validateNumberInput);


fullName.addEventListener("keydown", onlyPersianLetters);
province.addEventListener("keydown", onlyPersianLetters);
city.addEventListener("keydown", onlyPersianLetters);
fullName.addEventListener("input", validatePersianInput);
province.addEventListener("input", validatePersianInput);
city.addEventListener("input", validatePersianInput);

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
  } else if (discountCode.length > 50) {
    showToast("خطا", "کد تخفیف معتبر نیست.");
  } else {
    showToast("خطا", "لطفاً کد تخفیف را وارد کنید.");
  }

  const fullNameValue = fullName.value.trim();

  if (!fullNameValue) {
    showError("fullName", "نام و نام خانوادگی را وارد کنید.");
    isValid = false;
  } else if (fullNameValue.length < 3) {
    showError("fullName", "نام و نام خانوادگی باید حداقل ۳ کاراکتر باشد.");
    isValid = false;
  } else if (!/^[آ-ی\s‌-]+$/.test(fullNameValue)) {
    showError("fullName", "نام و نام خانوادگی باید فقط شامل حروف باشد.");
    isValid = false;
  }

  const phoneValue = phone.value.trim();

  if (!phoneValue) {
    showError("phone", "شماره همراه را وارد کنید.");
    isValid = false;
  } else if (!/^09\d{9}$/.test(phoneValue)) {
    showError("phone", "شماره همراه معتبر نیست.");
    isValid = false;
  }

  const emailValue = email.value.trim();

  if (emailValue && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailValue)) {
    showError("email", "ایمیل وارد شده معتبر نیست.");
    isValid = false;
  }

  function isValidIranianNationalCode(code) {
    if (!/^\d{10}$/.test(code)) {
      return false;
    }

    if (/^(\d)\1{9}$/.test(code)) {
      return false;
    }

    const check = Number(code[9]);

    let sum = 0;

    for (let i = 0; i < 9; i++) {
      sum += Number(code[i]) * (10 - i);
    }

    const remainder = sum % 11;

    const digit = remainder < 2 ? remainder : 11 - remainder;

    return digit === check;
  }

  const nationalCodeValue = nationalCode.value.trim();

  if (!nationalCodeValue) {
    showError("nationalCode", "کد ملی را وارد کنید.");
    isValid = false;
  } else if (!isValidIranianNationalCode(nationalCodeValue)) {
    showError("nationalCode", "کد ملی معتبر نیست.");
    isValid = false;
  }

  const provinceValue = province.value.trim();

  if (!provinceValue) {
    showError("province", "استان را وارد کنید.");
    isValid = false;
  } else if (!/^[آ-ی\s‌-]+$/.test(provinceValue)) {
    showError("province", "نام استان باید فقط شامل حروف باشد.");
    isValid = false;
  }

  const cityValue = city.value.trim();

  if (!cityValue) {
    showError("city", "شهر را وارد کنید.");
    isValid = false;
  } else if (!/^[آ-ی\s‌-]+$/.test(cityValue)) {
    showError("city", "نام شهر باید فقط شامل حروف باشد.");
    isValid = false;
  }

  const addressValue = address.value.trim();

  if (!addressValue) {
    showError("address", "آدرس را وارد کنید.");
    isValid = false;
  } else if (addressValue.length < 10) {
    showError("address", "آدرس وارد شده خیلی کوتاه است.");
    isValid = false;
  } else if (addressValue.length > 500) {
    showError("address", "آدرس نمی‌تواند بیشتر از ۵۰۰ کاراکتر باشد.");
    isValid = false;
  }

  const postalCodeValue = postalCode.value.trim();

  if (!postalCodeValue) {
    showError("postalCode", "کد پستی را وارد کنید.");
    isValid = false;
  } else if (!/^\d{10}$/.test(postalCodeValue)) {
    showError("postalCode", "کد پستی باید دقیقاً ۱۰ رقم باشد.");
    isValid = false;
  }

  const buildingNumberValue = buildingNumber.value.trim();

  if (!buildingNumberValue) {
    showError("buildingNumber", "شماره پلاک را وارد کنید.");
    isValid = false;
  } else if (!/^\d+$/.test(buildingNumberValue)) {
    showError("buildingNumber", "شماره پلاک معتبر نیست.");
    isValid = false;
  }

  const unitValue = unit.value.trim();

  if (unitValue && !/^\d+$/.test(unitValue)) {
    showError("unit", "شماره واحد معتبر نیست.");
    isValid = false;
  }

  // if (isValid) {
  //     // ارسال فرم به بک‌اند
  //     console.log("Form is valid");
  // }
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
