/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./apps/**/templates/**/*.html",
    "./static/src/ts/**/*.ts",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#fff7ed',
          100: '#ffedd5',
          200: '#fed7aa',
          300: '#fdba74',
          400: '#fb923c',
          500: '#f97316', // Primary vibrant orange
          600: '#ea580c',
          700: '#c2410c',
          800: '#9a3412',
          900: '#7c2d12',
          950: '#431407',
        },
        gov: {
          50: '#f4f7f5',  // Clean subtle minty-white surface
          100: '#e5ece7',
          200: '#cdd9d1',
          300: '#9fb5a6',
          400: '#6d8c76',
          500: '#4a6b54',
          600: '#324e3a',
          700: '#223828',
          800: '#14251a',
          900: '#0b1910', // Deep Forest Dark Green
          950: '#050d08', // Ultra Dark Green
        },
        navy: {
          800: '#14251a',
          900: '#0b1910',
        },
        forest: {
          50: '#f2f8f4',
          100: '#e1efe5',
          200: '#c4dfcd',
          300: '#9ac8a9',
          400: '#69a87d',
          500: '#448b59',
          600: '#317043',
          700: '#265735',
          800: '#1c4228',
          900: '#0b1910',
        }
      },
      fontFamily: {
        sans: ['Plus Jakarta Sans', 'Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}


