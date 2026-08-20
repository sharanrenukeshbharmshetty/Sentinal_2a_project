/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#0B0F19',
        card: '#111827',
        primary: '#00F5D4',
        secondary: '#3B82F6',
        highlight: '#A78BFA',
        textPrimary: '#E5E7EB',
        borderGlow: 'rgba(255,255,255,0.08)',
      },
      fontFamily: {
        sans: ['Inter', 'Roboto', 'sans-serif'],
      },
      boxShadow: {
        glow: '0 0 15px rgba(0, 245, 212, 0.4)',
        hover: '0 10px 25px rgba(0, 0, 0, 0.5)',
      }
    },
  },
  plugins: [],
}
