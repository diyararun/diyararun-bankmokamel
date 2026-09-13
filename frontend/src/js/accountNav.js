// ناوبری بدون رفرش کامل صفحه بین بخش‌های «حساب کاربری»
// (اطلاعات حساب کاربری / سفارش‌های من / آدرس‌های من).
//
// طراحی عمداً هیچ شاخه‌ی جداگانه‌ای در سمت سرور برای «درخواست AJAX»
// ندارد: هر سه ویو (profile_view، order_list_view، address_list_view و
// ...) همیشه همان صفحه‌ی کامل HTML همیشگی را برمی‌گردانند. این فایل فقط
// با fetch همان URL معمولی را می‌گیرد، با DOMParser بخش #accountWrapper
// را از داخل جواب استخراج می‌کند و به‌جای نسخه‌ی فعلی صفحه می‌گذارد.
// چون #accountWrapper هم سایدبار و هم محتوای اصلی را دربر می‌گیرد،
// یک جایگزینی ساده هم "فقط همان بخش رفرش شود" و هم "سایدبار همیشه بخش
// درستی را فعال نشان دهد" را همزمان حل می‌کند — نیازی به منطق جداگانه
// برای highlight کردن لینک فعال در جاوااسکریپت نیست، چون HTML تازه‌ای
// که از سرور می‌آید از قبل با active_page درست رندر شده.
//
// اگر جاوااسکریپت غیرفعال باشد یا چیزی خطا بدهد، همان <a href="..."> های
// معمولی کار می‌کنند و مرورگر به‌طور کامل صفحه را بارگذاری می‌کند —
// یعنی این کاملاً یک progressive enhancement است، نه یک وابستگی.

async function loadAccountSection(url, wrapper, push) {
  wrapper.setAttribute("aria-busy", "true");
  wrapper.classList.add("opacity-60", "pointer-events-none", "transition-opacity");

  let html;
  try {
    const response = await fetch(url, {
      headers: { "X-Requested-With": "XMLHttpRequest" },
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    html = await response.text();
  } catch (err) {
    console.error("بارگذاری بخش حساب کاربری ناموفق بود:", err);
    // به‌جای گیر کردن روی یک صفحه‌ی نصفه‌ونیمه، به روش قدیمی (ناوبری
    // کامل مرورگر) برمی‌گردیم — کاربر همچنان به مقصد می‌رسد.
    window.location.href = url;
    return;
  }

  const freshDoc = new DOMParser().parseFromString(html, "text/html");
  const freshWrapper = freshDoc.getElementById("accountWrapper");
  if (!freshWrapper) {
    // مثلاً کاربر لاگ‌اوت شده و سرور به صفحه‌ی ورود ریدایرکت کرده —
    // چنین جوابی #accountWrapper ندارد؛ به‌جای نمایش نصفه‌ونیمه، همان‌جا می‌رویم.
    window.location.href = url;
    return;
  }

  wrapper.replaceWith(freshWrapper);

  const freshTitle = freshDoc.querySelector("title");
  if (freshTitle) document.title = freshTitle.textContent;

  if (push) window.history.pushState({ accountNavUrl: url }, "", url);

  window.scrollTo({ top: 0, behavior: "smooth" });
}

document.addEventListener("click", (event) => {
  const link = event.target.closest(".js-account-nav");
  if (!link) return;

  // فقط وقتی صفحه‌ی فعلی خودش accountWrapper دارد این کلیک را می‌گیریم؛
  // مثلاً در صفحه‌ی «جزئیات سفارش» (order_detail.html) که این wrapper
  // را ندارد، همین لینک‌های سایدبار باید به شکل کاملاً عادی navigate کنند.
  const wrapper = document.getElementById("accountWrapper");
  if (!wrapper) return;

  event.preventDefault();
  loadAccountSection(link.href, wrapper, true);
});

window.addEventListener("popstate", () => {
  const wrapper = document.getElementById("accountWrapper");
  if (!wrapper) return;
  loadAccountSection(window.location.href, wrapper, false);
});
