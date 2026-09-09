import "./css/main.css";

import "./js/cartDrawer.js"; // addToCart, updateQuantity, openCartDrawer, closeCartDrawer
import "./js/toast.js"; // showToast
import "./js/mobileMenu.js"; // toggleMobileMenu
import "./js/profileMenu.js"; // toggleProfileMenu
import { initHeaderSearch } from "./js/headerSearch.js";
import { initProfileMenu } from "./js/profileMenu.js";
import "./js/categoryDrawer.js";

document.addEventListener("DOMContentLoaded", () => {
  initHeaderSearch();
  initProfileMenu();
});