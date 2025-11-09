module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        sidebar: "#2B2E33",
        mainbg: "#1E1F22",
        cardbg: "#2B2E33",
        popupbg: "#141416",
        gray: {
          950: '#030712',
        },
      },
      boxShadow: {
        'soft': '0 6px 18px rgba(0,0,0,0.6)',
        'neon': '0 6px 30px rgba(59,130,246,0.16)'
      },
      fontFamily: {
        sans: ['Inter var', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
    }
  },
  plugins: [],
  corePlugins: {
    preflight: true,
  },
  darkMode: 'class',
}

