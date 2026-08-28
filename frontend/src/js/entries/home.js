function toggleFaq(button) {
  const content = button.nextElementSibling;
  const svg = button.querySelector("svg");

  if (content.style.maxHeight && content.style.maxHeight !== "0px") {
    content.style.maxHeight = "0px";
    svg.style.transform = "rotate(0deg)";
  } else {
    // بستن بقیه FAQ ها
    document
      .querySelectorAll(".faq-content")
      .forEach((item) => (item.style.maxHeight = "0px"));
    document.querySelectorAll(".faq-content").forEach((item) => {
      const btnSvg = item.previousElementSibling.querySelector("svg");
      if (btnSvg) btnSvg.style.transform = "rotate(0deg)";
    });

    content.style.maxHeight = content.scrollHeight + "px";
    svg.style.transform = "rotate(180deg)";
  }
}
window.toggleFaq = toggleFaq;

function initSliders() {
  const bestSlider = document.getElementById("bestSlider");
  if (bestSlider) {
    document
      .getElementById("bestNext")
      ?.addEventListener("click", () =>
        bestSlider.scrollBy({ left: -300, behavior: "smooth" }),
      );
    document
      .getElementById("bestPrev")
      ?.addEventListener("click", () =>
        bestSlider.scrollBy({ left: 300, behavior: "smooth" }),
      );
  }

  const discSlider = document.getElementById("discSlider");
  if (discSlider) {
    document
      .getElementById("discNext")
      ?.addEventListener("click", () =>
        discSlider.scrollBy({ left: -300, behavior: "smooth" }),
      );
    document
      .getElementById("discPrev")
      ?.addEventListener("click", () =>
        discSlider.scrollBy({ left: 300, behavior: "smooth" }),
      );
  }
}

document.addEventListener("DOMContentLoaded", initSliders);
