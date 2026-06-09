/** @type {import('tailwindcss').Config} */
export default {
  content: ["./app/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        snowflake: { blue: '#29B5E8', dark: '#1B2A4A', accent: '#00D4AA' }
      }
    }
  },
  plugins: []
}
