import "../../css/contact.css";

import { showToast } from "../toast.js";

const fullName = document.getElementById("fullName");
const phone = document.getElementById("phone");
const email = document.getElementById("email");
const message = document.getElementById("message");


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


phone.addEventListener("keydown", onlyNumbers);
phone.addEventListener("input", validateNumberInput);

fullName.addEventListener("keydown", onlyPersianLetters);
fullName.addEventListener("input", validatePersianInput);

function handleContactSubmit(e) {
  e.preventDefault();
  showToast(
    "پیام ارسال شد",
    "پیام شما با موفقیت دریافت شد. کارشناسان ما به زودی با شما تماس خواهند گرفت.",
  );
  e.target.reset();

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

  const messageValue = message.value.trim();

  if (!messageValue) {
    showError("message", "متن پیام را وارد کنید.");
    isValid = false;
  } else if (messageValue.length < 5) {
    showError("message", "متن پیام باید حداقل ۵ کاراکتر باشد.");
    isValid = false;
  } else if (messageValue.length > 500) {
    showError("message", "متن پیام نمی‌تواند بیشتر از ۵۰۰ کاراکتر باشد.");
    isValid = false;
  }
}

window.handleContactSubmit = handleContactSubmit;
