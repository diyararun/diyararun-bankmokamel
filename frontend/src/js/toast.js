// اعلان (Toast) - مشترک در تمام صفحات
export function showToast(title, desc) {
  const toast = document.getElementById("toast");
  if (!toast) return;

  document.getElementById("toastTitle").innerText = title;
  document.getElementById("toastDesc").innerText = desc;

  toast.classList.remove("translate-y-20", "opacity-0", "pointer-events-none");
  toast.classList.add("translate-y-0", "opacity-100");

  setTimeout(() => {
    toast.classList.remove("translate-y-0", "opacity-100");
    toast.classList.add("translate-y-20", "opacity-0", "pointer-events-none");
  }, 3000);
}

// در دسترس بودن سراسری برای onclick های داخل HTML (تولیدشده توسط جنگو)
window.showToast = showToast;
