import { defineConfig } from "vite";
import { resolve } from "path";

// پیکربندی Vite برای کار با django-vite
// خروجی build در frontend/dist قرار می‌گیرد و توسط جنگو از طریق
// django-vite (تنظیمات DJANGO_VITE در backend/config/settings.py) خوانده می‌شود.
export default defineConfig({
  base: "/static/",
  server: {
    host: "localhost",
    port: 5173,
    strictPort: true,
    // برای این‌که مرورگر اجازه‌ی درخواست کراس-اوریجین از localhost:8000 (جنگو) را بدهد
    cors: true,
    origin: "http://localhost:5173",
  },
  build: {
    manifest: true,
    outDir: resolve(__dirname, "dist"),
    emptyOutDir: true,
    rollupOptions: {
      input: {
        main: resolve(__dirname, "src/main.js"),
        home: resolve(__dirname, "src/js/entries/home.js"),
        products: resolve(__dirname, "src/js/entries/products.js"),
        productDetail: resolve(__dirname, "src/js/entries/productDetail.js"),
        about: resolve(__dirname, "src/js/entries/about.js"),
        contact: resolve(__dirname, "src/js/entries/contact.js"),
        checkout: resolve(__dirname, "src/js/entries/checkout.js"),
        auth: resolve(__dirname, "src/js/entries/auth.js"),
        profile: resolve(__dirname, "src/js/entries/profile.js"),
      },
    },
  },
});
