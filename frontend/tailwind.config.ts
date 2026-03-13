import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "#0b1020",
        foreground: "#f1f5f9",
        card: "#121933",
        muted: "#94a3b8",
        brand: "#4f46e5",
        success: "#16a34a",
        warning: "#f59e0b",
      },
      borderRadius: {
        lg: "0.75rem",
        xl: "1rem",
      },
    },
  },
  plugins: [],
};

export default config;
