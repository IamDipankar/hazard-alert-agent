/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: { 50: '#eff6ff', 100: '#dbeafe', 200: '#bfdbfe', 300: '#93c5fd', 400: '#60a5fa', 500: '#3b82f6', 600: '#2563eb', 700: '#1d4ed8', 800: '#1e40af', 900: '#1e3a8a' },
        danger: { 50: '#fff1f2', 100: '#ffe4e6', 400: '#fb7185', 500: '#f43f5e', 600: '#e11d48', 700: '#be123c' },
        success: { 50: '#f0fdf4', 400: '#4ade80', 500: '#22c55e', 600: '#16a34a' },
        warning: { 50: '#fffbeb', 400: '#fbbf24', 500: '#f59e0b', 600: '#d97706' },
        slate: { 50: '#f8fafc', 100: '#f1f5f9', 200: '#e2e8f0', 300: '#cbd5e1', 400: '#94a3b8', 500: '#64748b', 600: '#475569', 700: '#334155', 800: '#1e293b', 900: '#0f172a', 950: '#020617' },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        bengali: ['Noto Sans Bengali', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
