/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: { sans: ['Inter', 'system-ui', 'sans-serif'], mono: ['JetBrains Mono', 'monospace'] },
      colors: {
        base: '#08080f', surface: '#0f0f1e', card: '#13132a',
        accent: { DEFAULT: '#7c6ff7', light: '#a99ff5', secondary: '#5a8cf8' },
      },
      animation: { 'fade-up': 'fadeUp 0.4s ease both', 'glow': 'glow 2s ease-in-out infinite' },
      keyframes: {
        fadeUp: { from: { opacity: 0, transform: 'translateY(12px)' }, to: { opacity: 1, transform: 'translateY(0)' } },
        glow: { '0%,100%': { boxShadow: '0 0 16px rgba(124,111,247,0.35)' }, '50%': { boxShadow: '0 0 32px rgba(124,111,247,0.6)' } },
      }
    }
  },
  plugins: []
}
