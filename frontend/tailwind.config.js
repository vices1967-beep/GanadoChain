import tailwindcss from "@tailwindcss/vite"

/** @type {import("tailwindcss").Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: "#f0fdf4",
          500: "#22c55e",
          600: "#16a34a",
        }
      }
    },
  },
  plugins: [],
}
