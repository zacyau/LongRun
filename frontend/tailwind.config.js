/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#1a1a1a',
        secondary: '#555555',
        muted: '#999999',
        border: '#e8e8e8',
        surface: '#f5f5f5',
      }
    },
  },
  plugins: [],
}