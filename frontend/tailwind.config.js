/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"DM Sans"', "system-ui", "sans-serif"],
        display: ['"Instrument Sans"', '"DM Sans"', "system-ui", "sans-serif"],
      },
      colors: {
        metro: {
          bg: "#070b14",
          panel: "#111827",
          border: "#1e3a5f",
          accent: "#0ea5e9",
        },
      },
      animation: {
        "pulse-slow": "pulse 2.5s cubic-bezier(0.4, 0, 0.6, 1) infinite",
      },
    },
  },
  plugins: [],
};
