// import { showToast } from "./toast.js";

// // اینپوت سرچ بازشونده در هدر
// export function initHeaderSearch() {
//   const searchBtn = document.getElementById("searchBtn");
//   const searchInput = document.getElementById("searchInput");
//   if (!searchBtn || !searchInput) return;

//   searchBtn.addEventListener("click", () => {
//     if (searchInput.classList.contains("w-0")) {
//       searchInput.classList.remove("w-0", "opacity-0");
//       searchInput.classList.add("w-48", "sm:w-64", "opacity-100");
//       searchInput.focus();
//     } else {
//       if (searchInput.value.trim() !== "") {
//         showToast("جستجو", `در حال جستجو برای: ${searchInput.value}`);
//       } else {
//         searchInput.classList.remove("w-48", "sm:w-64", "opacity-100");
//         searchInput.classList.add("w-0", "opacity-0");
//       }
//     }
//   });
// }




import { showToast } from "./toast.js";

// اینپوت سرچ بازشونده در هدر
export function initHeaderSearch() {
  const searchBtn = document.getElementById("searchBtn");
  const searchInput = document.getElementById("searchInput");
  const searchWrapper = document.getElementById("searchWrapper");
  if (!searchBtn || !searchInput) return;

  // تابع بسته کردن اینپوت
  const closeSearch = () => {
    searchInput.classList.remove("w-48", "sm:w-64", "opacity-100");
    searchInput.classList.add("w-0", "opacity-0", "pointer-events-none");
  };

  // تابع باز کردن اینپوت
  const openSearch = () => {
    searchInput.classList.remove("w-0", "opacity-0", "pointer-events-none");
    searchInput.classList.add("w-48", "sm:w-64", "opacity-100");
    searchInput.focus();
  };

  // تابع انجام عمل سرچ
  const performSearch = () => {
    const query = searchInput.value.trim();
    if (query !== "") {
      showToast("جستجو", `در حال جستجو برای: ${query}`);
    }
  };

  // کلیک روی دکمه سرچ
  searchBtn.addEventListener("click", (e) => {
    e.stopPropagation(); // جلوگیری از انتشار کلیک به document
    if (searchInput.classList.contains("w-0")) {
      openSearch();
    } else {
      if (searchInput.value.trim() !== "") {
        performSearch();
      } else {
        closeSearch();
      }
    }
  });

  // جلوگیری از بسته‌شدن هنگام کلیک داخل خود اینپوت
  searchInput.addEventListener("click", (e) => {
    e.stopPropagation();
  });

  // اجرای سرچ با کلید Enter
  searchInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      performSearch();
    } else if (e.key === "Escape") {
      // (اختیاری) بستن اینپوت با کلید Escape
      closeSearch();
    }
  });

  // بستن اینپوت هنگام کلیک در هر جای دیگری از صفحه
  document.addEventListener("click", (e) => {
    if (!searchInput.classList.contains("w-0")) {
      closeSearch();
    }
  });
}