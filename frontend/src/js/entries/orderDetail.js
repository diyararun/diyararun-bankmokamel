import { toPersianDigits } from "../formatToman.js";

// ======================== شمارشِ معکوسِ زنده‌ی مهلتِ رزرو (نشست ۴۴) ========================
//
// پس‌زمینه: از نشست ۴۳، موجودیِ کالاهای یک سفارشِ «در انتظار پرداخت» فوراً
// در لحظه‌ی checkout کم می‌شود و فقط تا یک مهلتِ مشخص (پیش‌فرض ۲۰ دقیقه،
// قابل‌تغییر از پنل ادمین — CheckoutSettings.reservation_minutes) برای
// همان مشتری نگه داشته می‌شود؛ بعدش سرور (چه به‌صورتِ تنبل، چه از طریقِ
// crontab) خودش سفارش را لغو و موجودی را برمی‌گرداند.
//
// تا قبل از این نشست، کاربر فقط یک ساعتِ مطلق می‌دید («تا ۱۴:۳۲ رزرو
// شده») و باید خودش تفریق می‌کرد ببیند دقیقاً چقدر وقت دارد. این فایل
// همان مهلت را به یک شمارشِ معکوسِ زنده (mm:ss) تبدیل می‌کند، دقیقاً کنار
// دکمه‌ی پرداخت.
//
// نکته‌ی مهم: این‌جا هیچ عددی (نه ۲۰ دقیقه، نه چیزِ دیگری) هاردکد نشده.
// data-deadline-ts روی #reservationCountdownBox همان Unix timestampی
// است که order.reservation_deadline در سرور، بر اساسِ تنظیماتِ واقعیِ
// CheckoutSettings، محاسبه کرده — این فایل فقط "تا آن لحظه چقدر مانده"
// را می‌شمارد، هرچه آن عدد باشد.
//
// این تایمر خودش هیچ‌چیزی را لغو نمی‌کند — لغوِ واقعیِ سفارش همچنان
// فقط کارِ سرور است (Order.release_expired_pending_orders). وقتی شمارش
// به صفر برسد، این فایل فقط صفحه را دوباره بارگذاری می‌کند تا وضعیتِ
// واقعیِ سفارش (که تا آن لحظه، با فراخوانیِ همان متد در ابتدای
// order_detail_view، قطعاً به‌روز شده) از سرور خوانده شود — به‌جای
// این‌که کاربر با یک دکمه‌ی «پرداخت» که ظاهراً هنوز فعال است اما دیگر
// اثری ندارد، سردرگم بماند.

function formatRemaining(ms) {
  const totalSeconds = Math.max(0, Math.floor(ms / 1000));
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  const text = `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
  return toPersianDigits(text);
}

function initReservationCountdown() {
  const box = document.getElementById("reservationCountdownBox");
  const display = document.getElementById("reservationCountdown");
  if (!box || !display) return;

  const deadlineMs = Number(box.dataset.deadlineTs) * 1000;
  if (!Number.isFinite(deadlineMs) || deadlineMs <= 0) return;

  let reloaded = false;
  let intervalId = null;

  function tick() {
    const remaining = deadlineMs - Date.now();
    display.textContent = formatRemaining(remaining);

    if (remaining <= 0) {
      if (intervalId) clearInterval(intervalId);
      if (!reloaded) {
        reloaded = true;
        box.classList.remove("border-amber-300");
        box.classList.add("border-red-300", "bg-red-50");
        window.setTimeout(() => window.location.reload(), 1200);
      }
    }
  }

  tick();
  intervalId = setInterval(tick, 1000);
}

document.addEventListener("DOMContentLoaded", initReservationCountdown);
