/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#18212f",
        line: "#d8dee8",
        surface: "#f7f9fc",
        brand: "#0f766e",
        accent: "#2563eb",
        warning: "#d97706",
        danger: "#dc2626"
      },
      boxShadow: {
        soft: "0 10px 30px rgba(24, 33, 47, 0.08)"
      }
    }
  },
  plugins: []
};

