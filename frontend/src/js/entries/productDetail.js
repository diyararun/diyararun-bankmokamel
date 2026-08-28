import "../../css/product-detail.css";

import { addMultipleToCart } from "../cartDrawer.js";
import { showToast } from "../toast.js";

let currentQuantity = 1;
const productImageHTML =
  '<img class="w-full h-full object-cover" src="./test4.webp" alt="" />';
const galleryImages = [
  productImageHTML,
  productImageHTML,
  productImageHTML,
  productImageHTML,
  productImageHTML,
  productImageHTML,
];
let currentGalleryIndex = 0;

// این آرایه به‌جای «cart» عمومی (که حالا در cartDrawer.js مدیریت می‌شود) فقط
// برای شمارش تعداد همین محصول در حال افزودن استفاده می‌شود.
function renderThumbnails() {
  const container = document.getElementById("thumbnailsContainer");
  if (!container) return;
  container.innerHTML = "";

  const maxVisible = 4;
  const total = galleryImages.length;

  for (let i = 0; i < Math.min(total, maxVisible); i++) {
    const isLastAndHasMore = i === maxVisible - 1 && total > maxVisible;
    const button = document.createElement("button");

    if (isLastAndHasMore) {
      const remaining = total - maxVisible + 1;
      button.className =
        "thumb-btn h-16 bg-slate-100 rounded-xl border border-slate-200 flex items-center justify-center relative overflow-hidden group backdrop-blur-sm";
      button.innerHTML = `
        <div class="w-full h-full opacity-40 blur-[1px] select-none">${galleryImages[i]}</div>
        <div class="absolute inset-0 bg-slate-900/60 flex flex-col items-center justify-center text-white font-black text-xs group-hover:bg-red-600/80 transition-colors">
          <span>...</span>
          <span class="text-[10px] font-medium">+${remaining} عکس</span>
        </div>
      `;
      button.onclick = () => {
        currentGalleryIndex = i;
        openGalleryModal();
      };
    } else {
      const isSelected = i === currentGalleryIndex;
      button.className = `thumb-btn h-16 bg-slate-50 rounded-xl flex items-center justify-center overflow-hidden transition-all ${
        isSelected
          ? "border-2 border-red-600"
          : "border border-slate-200 hover:border-slate-300"
      }`;
      button.innerHTML = galleryImages[i];
      button.onclick = () => selectImage(i);
    }

    container.appendChild(button);
  }
}

function selectImage(index) {
  currentGalleryIndex = index;
  document.getElementById("mainImageEmoji").innerHTML = galleryImages[index];
  renderThumbnails();
}

function openGalleryModal() {
  updateGalleryModalContent();
  const modal = document.getElementById("galleryModal");
  modal.classList.remove("opacity-0", "pointer-events-none");
  modal.classList.add("opacity-100");
}

function closeGalleryModal() {
  const modal = document.getElementById("galleryModal");
  modal.classList.remove("opacity-100");
  modal.classList.add("opacity-0", "pointer-events-none");
}

function changeGalleryImageWithAnimation(nextIndex) {
  const container = document.getElementById("modalEmojiContainer");
  container.classList.add("modal-img-hidden");

  setTimeout(() => {
    currentGalleryIndex = nextIndex;
    selectImage(currentGalleryIndex);
    updateGalleryModalContent();
    container.classList.remove("modal-img-hidden");
  }, 200);
}

function nextGalleryImage() {
  const nextIndex = (currentGalleryIndex + 1) % galleryImages.length;
  changeGalleryImageWithAnimation(nextIndex);
}

function prevGalleryImage() {
  const prevIndex =
    (currentGalleryIndex - 1 + galleryImages.length) % galleryImages.length;
  changeGalleryImageWithAnimation(prevIndex);
}

function updateGalleryModalContent() {
  document.getElementById("modalEmojiContainer").innerHTML =
    galleryImages[currentGalleryIndex];
  document.getElementById("modalImageCaption").innerText =
    `تصویر ${currentGalleryIndex + 1} از ${galleryImages.length} - وی گلد استاندارد`;
}

function switchTab(tabKey) {
  const contents = document.querySelectorAll(".tab-content");
  contents.forEach((el) => el.classList.remove("active"));

  document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.classList.remove("text-red-600", "border-red-600");
    btn.classList.add("text-slate-500", "border-transparent");
  });

  const activeContent = document.getElementById(`tabContent-${tabKey}`);
  activeContent.classList.add("active");

  const activeBtn = document.getElementById(`tabBtn-${tabKey}`);
  activeBtn.classList.remove("text-slate-500", "border-transparent");
  activeBtn.classList.add("text-red-600", "border-red-600");
}

function adjustQuantity(delta) {
  currentQuantity += delta;
  if (currentQuantity < 1) currentQuantity = 1;
  document.getElementById("detailQuantity").innerText = currentQuantity;
}

function addCurrentProductToCart() {
  // TODO: وقتی مدل Product در جنگو اضافه شد، نام/قیمت/اسلاگ واقعی محصول
  // باید از context صفحه (به‌جای مقادیر ثابت) خوانده شود.
  const productName = "وی گلد استاندارد 100%";
  const productPrice = 3570000;

  addMultipleToCart(productName, productPrice, galleryImages[0], currentQuantity);
  showToast(
    "افزوده شد به سبد",
    `${currentQuantity} عدد «${productName}» به سبد اضافه شد.`,
  );
}

window.selectImage = selectImage;
window.openGalleryModal = openGalleryModal;
window.closeGalleryModal = closeGalleryModal;
window.nextGalleryImage = nextGalleryImage;
window.prevGalleryImage = prevGalleryImage;
window.switchTab = switchTab;
window.adjustQuantity = adjustQuantity;
window.addCurrentProductToCart = addCurrentProductToCart;

document.addEventListener("DOMContentLoaded", () => {
  renderThumbnails();

  const relatedSlider = document.getElementById("relatedSlider");
  if (relatedSlider) {
    document
      .getElementById("relatedNext")
      ?.addEventListener("click", () =>
        relatedSlider.scrollBy({ left: -280, behavior: "smooth" }),
      );
    document
      .getElementById("relatedPrev")
      ?.addEventListener("click", () =>
        relatedSlider.scrollBy({ left: 280, behavior: "smooth" }),
      );
  }
});
