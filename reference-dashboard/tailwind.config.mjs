/** @type {import('tailwindcss').Config} */
export default {
  content: ["./src/**/*.{astro,html,js,jsx,ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        serif: ["Fraunces", "Georgia", "serif"],
      },
      colors: {
        brand: {
          50: "#f5f7ff",
          100: "#e8edff",
          500: "#5b6ef0",
          600: "#4452d9",
          900: "#1a1f4a",
        },
      },
    },
  },
  plugins: [],
};
