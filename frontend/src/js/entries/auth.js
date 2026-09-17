import "../../css/auth.css";

import { showToast } from "../toast.js";
import { postForm } from "../csrf.js";

let timerInterval = null;
let timeLeft = 120; // ۲ دقیقه
let currentPhone = "";

// مرحله‌ی اول: ارسال شماره و درخواست کد از بک‌اند جنگو
async function handleSendOtp(e) {
  e.preventDefault();
  const phone = document.getElementById("userPhone").value.trim();

  // نشست ۴۸: قبلاً اگر پاسخِ سرور یک خطای ۵۰۰ (صفحه‌ی HTML، نه JSON) بود،
  // postForm روی response.json() کرش می‌کرد، این await هیچ‌وقت resolve
  // نمی‌شد، و از دیدِ کاربر دکمه اصلاً «کار نمی‌کرد» — بدونِ هیچ پیام یا
  // خطایی. حالا حداقل یک toast نشان داده می‌شود (دقیقاً همان الگویی که
  // فرم کدِ تخفیف در checkout.js از قبل داشت).
  let result;
  try {
    result = await postForm("/accounts/otp/request/", { phone });
  } catch (err) {
    showToast("خطا", "خطا در برقراری ارتباط با سرور. دوباره تلاش کنید.");
    return;
  }

  if (!result.ok) {
    const message =
      (result.errors && result.errors.phone && result.errors.phone[0]) ||
      "شماره موبایل معتبر نیست.";
    showToast("خطا", message);
    return;
  }

  currentPhone = phone;
  document.getElementById("displayPhone").innerText = phone;

  document.getElementById("stepPhone").classList.add("hidden");
  document.getElementById("stepOtp").classList.remove("hidden");

  startTimer();
  setupOtpAutoTab();
  showToast("کد ارسال شد", `کد تأیید به شماره ${phone} ارسال گردید.`);
}

function goToStepPhone() {
  clearInterval(timerInterval);
  document.getElementById("stepOtp").classList.add("hidden");
  document.getElementById("stepPhone").classList.remove("hidden");
}

function startTimer() {
  timeLeft = 120;
  const timerBox = document.getElementById("timerBox");
  const resendBtn = document.getElementById("resendBtn");
  resendBtn.disabled = true;

  clearInterval(timerInterval);
  timerInterval = setInterval(() => {
    timeLeft--;
    const minutes = String(Math.floor(timeLeft / 60)).padStart(2, "0");
    const seconds = String(timeLeft % 60).padStart(2, "0");
    timerBox.innerText = `${minutes}:${seconds}`;

    if (timeLeft <= 0) {
      clearInterval(timerInterval);
      timerBox.innerText = "00:00";
      resendBtn.disabled = false;
    }
  }, 1000);
}

async function resendOtpCode() {
  const result = await postForm("/accounts/otp/request/", {
    phone: currentPhone,
  });
  if (!result.ok) {
    showToast("خطا", "ارسال مجدد ناموفق بود. دوباره تلاش کنید.");
    return;
  }
  startTimer();
  showToast("ارسال مجدد کد", "کد جدید برای شما پیامک شد.");
}

function setupOtpAutoTab() {
  const inputs = document.querySelectorAll(".otp-input");
  inputs[0].focus();

  inputs.forEach((input, index) => {
    input.addEventListener("input", (e) => {
      const val = e.target.value;
      if (val.length === 1 && index < inputs.length - 1) {
        inputs[index + 1].focus();
      }
    });

    input.addEventListener("keydown", (e) => {
      if (e.key === "Backspace" && !input.value && index > 0) {
        inputs[index - 1].focus();
      }
    });

    input.addEventListener("paste", (e) => {
      e.preventDefault();
      const pasteData = (e.clipboardData || window.clipboardData)
        .getData("text")
        .trim();
      if (/^\d+$/.test(pasteData)) {
        const digits = pasteData.split("");
        inputs.forEach((inp, i) => {
          if (digits[i]) inp.value = digits[i];
        });
        if (digits.length >= inputs.length) {
          inputs[inputs.length - 1].focus();
        }
      }
    });
  });
}

// مرحله‌ی دوم: تایید کد از طریق بک‌اند جنگو (لاگین/ثبت‌نام واقعی + session)
async function handleVerifyOtp(e) {
  e.preventDefault();
  const inputs = document.querySelectorAll(".otp-input");
  let code = "";
  inputs.forEach((i) => (code += i.value));

  if (code.length < 5) {
    showToast("خطا", "لطفاً تمامی ۵ رقم کد را وارد کنید.");
    return;
  }

  let result;
  try {
    result = await postForm("/accounts/otp/verify/", {
      phone: currentPhone,
      code,
      // Passed through from LoginRequiredMixin's own redirect (?next=...)
      // when the user was sent here from a page like checkout — without
      // this, verify_otp has no way to know where to send them back.
      next: new URLSearchParams(window.location.search).get("next") || "",
    });
  } catch (err) {
    // نشست ۴۸: همان دلیلِ کامنتِ بالا در handleSendOtp — بدونِ این catch،
    // یک خطای سمتِ سرور یعنی دکمه‌ی «تأیید و ورود به حساب» ظاهراً هیچ
    // واکنشی نشان نمی‌دهد.
    showToast("خطا", "خطا در برقراری ارتباط با سرور. دوباره تلاش کنید.");
    return;
  }

  if (!result.ok) {
    showToast("خطا", result.message || "کد تأیید نادرست است.");
    return;
  }

  showToast(
    "خوش آمدید",
    "ورود با موفقیت انجام شد. در حال انتقال به فروشگاه...",
  );
  setTimeout(() => {
    window.location.href = result.redirect_url || "/";
  }, 1500);
}

// ======================== مودالِ «شرایط و قوانین» (نشست ۵۰) ========================
//
// همان الگویِ باز/بسته‌شدنِ کشوی سبدِ خرید (cartDrawer.js: opacity-0 +
// pointer-events-none ↔ opacity-100) — نه چیزی جدید، فقط برای یک مودالِ
// وسط‌چین به‌جای یک کشوی کناری.
function openTermsModal(e) {
  if (e) e.preventDefault();
  const modal = document.getElementById("termsModal");
  if (!modal) return;
  modal.classList.remove("opacity-0", "pointer-events-none");
  modal.classList.add("opacity-100");
}

function closeTermsModal() {
  const modal = document.getElementById("termsModal");
  if (!modal) return;
  modal.classList.remove("opacity-100");
  modal.classList.add("opacity-0", "pointer-events-none");
}

document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") closeTermsModal();
});

window.handleSendOtp = handleSendOtp;
window.goToStepPhone = goToStepPhone;
window.resendOtpCode = resendOtpCode;
window.handleVerifyOtp = handleVerifyOtp;
window.openTermsModal = openTermsModal;
window.closeTermsModal = closeTermsModal;