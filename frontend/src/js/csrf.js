// خواندن توکن CSRF جنگو برای درخواست‌های fetch (از متای صفحه که در base.html قرار دارد)
export function getCsrfToken() {
  const meta = document.querySelector('meta[name="csrf-token"]');
  return meta ? meta.getAttribute("content") : "";
}

export async function postForm(url, data) {
  const body = new URLSearchParams(data);
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
      "X-CSRFToken": getCsrfToken(),
    },
    body,
  });
  return response.json();
}
