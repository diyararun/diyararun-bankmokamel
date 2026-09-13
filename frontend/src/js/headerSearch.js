// اینپوت سرچ بازشونده در هدر + Live Search
//
// جریان کار: با هر بار تایپ (با یک تاخیر کوتاه/debounce تا فشار روی سرور
// زیاد نشود) یک درخواست به /products/search/?q=... زده می‌شود که در
// apps/catalog/views.py (ProductSearchSuggestView) تعریف شده و یک لیست
// کوتاه JSON از محصولات مطابق برمی‌گرداند. نتیجه به‌صورت یک دراپ‌داون زیر
// اینپوت رندر می‌شود. زدن Enter یا کلیک روی «مشاهده همه نتایج» کاربر را به
// صفحه‌ی /products/?q=... می‌برد که همان متن را روی کل محصولات فیلتر می‌کند
// (ProductListView در همان ویو).

import { formatToman } from "./formatToman.js";

const SEARCH_ENDPOINT = "/products/search/";
const PRODUCTS_URL = "/products/";
const DEBOUNCE_MS = 300;
const MIN_QUERY_LENGTH = 2;

export function initHeaderSearch() {
  const searchBtn = document.getElementById("searchBtn");
  const searchInput = document.getElementById("searchInput");
  const searchResults = document.getElementById("searchResults");
  if (!searchBtn || !searchInput) return;

  let debounceTimer = null;
  let latestRequestId = 0; // برای نادیده گرفتن جواب‌های دیر رسیده و قدیمی

  // تابع بسته کردن اینپوت
  const closeSearch = () => {
    searchInput.classList.remove("w-48", "sm:w-64", "opacity-100");
    searchInput.classList.add("w-0", "opacity-0", "pointer-events-none");
    hideResults();
  };

  // تابع باز کردن اینپوت
  const openSearch = () => {
    searchInput.classList.remove("w-0", "opacity-0", "pointer-events-none");
    searchInput.classList.add("w-48", "sm:w-64", "opacity-100");
    searchInput.focus();
  };

  const hideResults = () => {
    if (!searchResults) return;
    searchResults.classList.add("hidden");
    searchResults.innerHTML = "";
  };

  const showResults = () => {
    if (!searchResults) return;
    searchResults.classList.remove("hidden");
  };

  // رفتن به صفحه‌ی نتایج کامل با همین متن جستجو
  const goToFullResults = (query) => {
    window.location.href = `${PRODUCTS_URL}?q=${encodeURIComponent(query)}`;
  };

  const renderLoading = () => {
    if (!searchResults) return;
    searchResults.innerHTML = `
      <div class="p-4 text-center text-xs text-slate-400">در حال جستجو...</div>
    `;
    showResults();
  };

  const renderEmpty = (query) => {
    if (!searchResults) return;
    searchResults.innerHTML = `
      <div class="p-4 text-center text-xs text-slate-400">
        محصولی برای «${escapeHtml(query)}» پیدا نشد.
      </div>
    `;
    showResults();
  };

  const renderResults = (query, products) => {
    if (!searchResults) return;

    const items = products
      .map(
        (p) => `
        <a
          href="${p.url}"
          class="flex items-center gap-3 p-3 hover:bg-slate-50 transition-colors border-b border-slate-100 last:border-b-0"
        >
          <div class="w-12 h-12 shrink-0 rounded-lg bg-slate-100 overflow-hidden">
            ${
              p.image
                ? `<img src="${p.image}" alt="${escapeHtml(p.name)}" class="w-full h-full object-cover" />`
                : ""
            }
          </div>
          <div class="min-w-0 flex-1">
            <p class="text-sm font-bold text-slate-900 truncate">${escapeHtml(p.name)}</p>
            <p class="text-[11px] text-slate-400 truncate">${escapeHtml(p.brand || "")}</p>
          </div>
          ${
            p.price
              ? `<span class="text-xs font-black text-red-600 shrink-0">${formatPrice(p.price)}<span class="text-[10px] font-normal text-slate-400"> تومان</span></span>`
              : ""
          }
        </a>`,
      )
      .join("");

    searchResults.innerHTML = `
      ${items}
      <button
        type="button"
        data-view-all
        class="w-full p-3 text-xs font-bold text-red-600 hover:bg-red-50 transition-colors text-center"
      >
        مشاهده همه نتایج برای «${escapeHtml(query)}»
      </button>
    `;

    searchResults.querySelector("[data-view-all]")?.addEventListener("click", (e) => {
      e.stopPropagation();
      goToFullResults(query);
    });

    showResults();
  };

  // درخواست به بک‌اند و رندر نتیجه؛ latestRequestId جلوی این را می‌گیرد که
  // جواب یک درخواست قدیمی‌تر (که دیرتر برگشته) نتیجه‌ی تازه‌تر را جایگزین کند.
  const fetchSuggestions = async (query) => {
    const requestId = ++latestRequestId;
    renderLoading();
    try {
      const response = await fetch(`${SEARCH_ENDPOINT}?q=${encodeURIComponent(query)}`);
      if (!response.ok) throw new Error("search request failed");
      const data = await response.json();
      if (requestId !== latestRequestId) return; // جواب قدیمی، نادیده گرفته شود

      if (!data.results || data.results.length === 0) {
        renderEmpty(query);
      } else {
        renderResults(query, data.results);
      }
    } catch (err) {
      if (requestId !== latestRequestId) return;
      hideResults();
    }
  };

  const handleInput = () => {
    const query = searchInput.value.trim();
    clearTimeout(debounceTimer);

    if (query.length < MIN_QUERY_LENGTH) {
      hideResults();
      return;
    }

    debounceTimer = setTimeout(() => fetchSuggestions(query), DEBOUNCE_MS);
  };

  // کلیک روی دکمه سرچ: بار اول باز می‌کند، بعد از آن (با متن پر) می‌رود به نتایج کامل
  searchBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    if (searchInput.classList.contains("w-0")) {
      openSearch();
    } else if (searchInput.value.trim() !== "") {
      goToFullResults(searchInput.value.trim());
    } else {
      closeSearch();
    }
  });

  searchInput.addEventListener("input", handleInput);

  // جلوگیری از بسته‌شدن هنگام کلیک داخل خود اینپوت/نتایج
  searchInput.addEventListener("click", (e) => e.stopPropagation());
  searchResults?.addEventListener("click", (e) => e.stopPropagation());

  searchInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      const query = searchInput.value.trim();
      if (query !== "") goToFullResults(query);
    } else if (e.key === "Escape") {
      closeSearch();
    }
  });

  // بستن اینپوت/نتایج هنگام کلیک در هر جای دیگری از صفحه
  document.addEventListener("click", () => {
    if (!searchInput.classList.contains("w-0")) {
      closeSearch();
    }
  });
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}

function formatPrice(value) {
  // Delegates to the site-wide formatToman() (comma-grouped, Persian
  // digits) instead of toLocaleString("fa-IR") — the built-in locale
  // formatting uses "٬" (the Arabic thousands separator) rather than a
  // plain comma, which didn't match how prices are formatted everywhere
  // else on the site.
  return formatToman(value);
}
