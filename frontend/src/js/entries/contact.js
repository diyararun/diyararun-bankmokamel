import "../../css/contact.css";

import { showToast } from "../toast.js";

function handleContactSubmit(e) {
  e.preventDefault();
  showToast(
    "پیام ارسال شد",
    "پیام شما با موفقیت دریافت شد. کارشناسان ما به زودی با شما تماس خواهند گرفت.",
  );
  e.target.reset();
}

window.handleContactSubmit = handleContactSubmit;
