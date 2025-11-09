/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'dark-bg': '#0a0a0a',
        'dark-panel': '#1a1a1a',
        'dark-border': '#2a2a2a',
        'dark-hover': '#3a3a3a',
      },
    },
  },
  plugins: [],
}

