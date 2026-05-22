/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'comcast-blue': '#0066CC',
        'comcast-darkblue': '#003366',
        'comcast-lightblue': '#E6F0FF',
      }
    },
  },
  plugins: [],
}
