import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#ffffff",
        foreground: "#111827",
        sidebar: {
          DEFAULT: "#f9fafb",
          border: "#f3f4f6",
          hover: "#f3f4f6",
          active: "#e5e7eb",
          foreground: "#374151"
        },
        primary: {
          50: '#f0fdf4',
          100: '#dcfce7',
          500: '#10b981',
          600: '#059669',
          700: '#047857',
          DEFAULT: '#10a37f', // ChatGPT emerald style
          foreground: '#ffffff',
        },
        muted: {
          DEFAULT: "#f3f4f6",
          foreground: "#6b7280",
        },
        border: "#e5e7eb",
        accent: {
          DEFAULT: "#f9fafb",
          foreground: "#111827",
        },
        card: {
          DEFAULT: "#ffffff",
          foreground: "#111827",
        }
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      boxShadow: {
        'subtle': '0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px 0 rgba(0, 0, 0, 0.03)',
        'float': '0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.02)',
      }
    },
  },
  plugins: [],
};
export default config;
