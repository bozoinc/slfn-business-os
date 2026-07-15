/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        foreground: "hsl(var(--foreground))",
        background: "hsl(var(--background))",
        primary: {
          DEFAULT: hsl(222.2 84% 4.9%),
          foreground: hsl(210 40% 98%),
        },
        secondary: {
          DEFAULT: hsl(210 40% 96%),
          foreground: hsl(222.2 84% 4.9%),
        },
        destructive: {
          DEFAULT: "hsl(0 84.3%60.4%)",
          foreground: "hsl(210 40% 98%)",
        },
        muted: {
          DEFAULT: "hsl(210 40% 96%)",
          foreground: "hsl(215 28% 17%)",
        },
        accent: {
          DEFAULT: "hsl(210 40% 96%)",
          foreground: "hsl(222.2 84% 4.9%)",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
    },
  },
  plugins: [],
}