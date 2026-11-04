import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // LearnMate Design System
        // Primary: Forest Ink (muted green)
        primary: {
          DEFAULT: "#2D6A4F",
          50:  "#EAF3EF",
          100: "#C6E0D4",
          200: "#9FCABC",
          300: "#78B4A3",
          400: "#52A090",
          500: "#2D6A4F",
          600: "#255A43",
          700: "#1C4A35",
          800: "#143A28",
          900: "#0C2A1B",
          foreground: "#FFFFFF",
        },
        // Background: warm paper
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        paper:  "#F5F0E8",
        ink:    "#1A1A1A",
        muted: {
          DEFAULT: "#6B7280",
          foreground: "#9CA3AF",
        },
        // Accent: Amber (streaks/achievements only)
        accent: {
          DEFAULT: "#E07B39",
          foreground: "#FFFFFF",
          50:  "#FDF3EC",
          100: "#FAE0CC",
          200: "#F5C099",
          300: "#F0A066",
          400: "#E88C50",
          500: "#E07B39",
          600: "#C06830",
          700: "#9E5526",
        },
        // shadcn/ui token overrides
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        border: "hsl(var(--border))",
        input:  "hsl(var(--input))",
        ring:   "hsl(var(--ring))",
        // State colors (topic progress trail)
        state: {
          "not-started": "#9CA3AF",
          "in-progress": "#3B82F6",
          practicing:    "#F59E0B",
          mastered:      "#2D6A4F",
        },
      },
      fontFamily: {
        serif:  ["DM Serif Display", "Georgia", "serif"],
        sans:   ["IBM Plex Sans", "system-ui", "sans-serif"],
        mono:   ["IBM Plex Mono", "Menlo", "monospace"],
      },
      fontSize: {
        "2xs": ["0.625rem", { lineHeight: "1rem" }],
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      boxShadow: {
        "ink-sm": "0 1px 3px 0 rgba(26, 26, 26, 0.08), 0 1px 2px -1px rgba(26, 26, 26, 0.06)",
        "ink-md": "0 4px 6px -1px rgba(26, 26, 26, 0.08), 0 2px 4px -2px rgba(26, 26, 26, 0.06)",
        "ink-lg": "0 10px 15px -3px rgba(26, 26, 26, 0.08), 0 4px 6px -4px rgba(26, 26, 26, 0.06)",
      },
      keyframes: {
        "fade-in": {
          "0%": { opacity: "0", transform: "translateY(4px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "mastered-pop": {
          "0%":   { transform: "scale(1)" },
          "50%":  { transform: "scale(1.15)" },
          "100%": { transform: "scale(1)" },
        },
        "trail-draw": {
          "0%":   { strokeDashoffset: "100" },
          "100%": { strokeDashoffset: "0" },
        },
        "slide-in-right": {
          "0%": { transform: "translateX(100%)", opacity: "0" },
          "100%": { transform: "translateX(0)", opacity: "1" },
        },
        "pulse-subtle": {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.7" },
        },
      },
      animation: {
        "fade-in":       "fade-in 0.2s ease-out",
        "mastered-pop":  "mastered-pop 0.4s ease-in-out",
        "trail-draw":    "trail-draw 0.6s ease-out forwards",
        "slide-right":   "slide-in-right 0.3s ease-out",
        "pulse-subtle":  "pulse-subtle 2s ease-in-out infinite",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;
