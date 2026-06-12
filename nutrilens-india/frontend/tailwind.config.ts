import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./pages/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./app/**/*.{ts,tsx}",
    "./src/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#FFF8F1",
        primary: {
          DEFAULT: "#C96A3D",
          foreground: "#FFFFFF",
          50: "#FDF0E8",
          100: "#F9D9C5",
          200: "#F2B390",
          300: "#E88D5A",
          400: "#DC7040",
          500: "#C96A3D",
          600: "#A8542F",
          700: "#863F22",
          800: "#642B15",
          900: "#421808",
        },
        secondary: {
          DEFAULT: "#E6B17E",
          foreground: "#1E1E1E",
        },
        accent: {
          DEFAULT: "#3F6B4B",
          foreground: "#FFFFFF",
          50: "#EBF3ED",
          100: "#C8E0CC",
          200: "#97C4A1",
          300: "#66A874",
          400: "#4D8A5C",
          500: "#3F6B4B",
          600: "#2F5237",
          700: "#1F3923",
          800: "#10200F",
          900: "#040805",
        },
        dark: "#1E1E1E",
        card: {
          DEFAULT: "#FFFFFF",
          foreground: "#1E1E1E",
        },
        success: "#4CAF50",
        muted: {
          DEFAULT: "#F5EDE3",
          foreground: "#6B5C4E",
        },
        border: "#E8D5C0",
        input: "#E8D5C0",
        ring: "#C96A3D",
        destructive: {
          DEFAULT: "#DC2626",
          foreground: "#FFFFFF",
        },
      },
      fontFamily: {
        heading: ["Lora", "Georgia", "serif"],
        body: ["Raleway", "system-ui", "sans-serif"],
        sans: ["Raleway", "system-ui", "sans-serif"],
      },
      borderRadius: {
        lg: "0.75rem",
        md: "0.5rem",
        sm: "0.375rem",
        xl: "1rem",
        "2xl": "1.5rem",
        "3xl": "2rem",
      },
      boxShadow: {
        soft: "0 2px 15px rgba(201, 106, 61, 0.08)",
        card: "0 4px 24px rgba(201, 106, 61, 0.1)",
        elevated: "0 8px 40px rgba(201, 106, 61, 0.15)",
        glow: "0 0 30px rgba(201, 106, 61, 0.2)",
      },
      backgroundImage: {
        "warm-gradient": "linear-gradient(135deg, #FFF8F1 0%, #FDF0E4 100%)",
        "card-gradient": "linear-gradient(135deg, #FFFFFF 0%, #FFF8F1 100%)",
        "hero-pattern": "radial-gradient(circle at 20% 50%, rgba(201,106,61,0.08) 0%, transparent 60%), radial-gradient(circle at 80% 20%, rgba(230,177,126,0.12) 0%, transparent 50%)",
      },
      animation: {
        "float": "float 6s ease-in-out infinite",
        "float-delay": "float 6s ease-in-out 2s infinite",
        "float-delay-2": "float 6s ease-in-out 4s infinite",
        "counter": "counter 1s ease-out forwards",
        "slide-up": "slideUp 0.5s ease-out forwards",
        "fade-in": "fadeIn 0.6s ease-out forwards",
      },
      keyframes: {
        float: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-20px)" },
        },
        slideUp: {
          from: { opacity: "0", transform: "translateY(20px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
        fadeIn: {
          from: { opacity: "0" },
          to: { opacity: "1" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
