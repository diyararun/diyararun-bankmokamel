/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "../backend/templates/**/*.html",
    // Page templates now live inside each app (apps/catalog/templates/,
    // apps/store/templates/, apps/accounts/templates/, apps/orders/templates/...)
    // instead of the single shared backend/templates/ folder — this glob
    // covers all of them.
    "../backend/apps/*/templates/**/*.html",
    "./src/**/*.js",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Vazirmatn", "sans-serif"],
      },
      colors: {
        brandRed: "#DC2626",
        brandDark: "#0F172A",
        brandGray: "#F8FAFC",
      },
      animation: {
        "infinite-scroll": "infinite-scroll 25s linear infinite",
        "bounce-short": "bounce-short 0.3s ease-in-out",
      },
      keyframes: {
        "infinite-scroll": {
          "0%": { transform: "translateX(0)" },
          "100%": { transform: "translateX(100%)" },
        },
        "bounce-short": {
          "0%, 100%": { transform: "scale(1)" },
          "50%": { transform: "scale(1.3)" },
        },
      },
    },
  },
  plugins: [],
};