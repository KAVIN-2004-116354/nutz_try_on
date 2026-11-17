/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        nutz: {
          bg: '#F5F4F8',
          surface: '#FFFFFF',
          text: '#171717',
          muted: '#475569',
          secondary: '#52525B',
          border: '#E8E8EF',
          accent: '#5B3DF0',
          'accent-hover': '#4B2EE0',
          'accent-light': '#F0EDFD',
          'accent-secondary': '#8F77F8',
          success: '#16A34A',
          error: '#DC2626',
        },
        studio: {
          950: '#06090F',
          900: '#090D16',
          850: '#0D121F',
          800: '#121829',
        },
        brand: {
          500: '#5B3DF0',
          600: '#4B2EE0',
          700: '#3D22C4',
        }
      },
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'Inter', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      boxShadow: {
        'subtle': '0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px 0 rgba(0, 0, 0, 0.03)',
        'card': '0 4px 20px -2px rgba(18, 24, 40, 0.05)',
        'card-hover': '0 12px 30px -4px rgba(91, 61, 240, 0.12)',
        'premium': '0 12px 28px -6px rgba(91, 61, 240, 0.3)',
      }
    },
  },
  plugins: [],
}
