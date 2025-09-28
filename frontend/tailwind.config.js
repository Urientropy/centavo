/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'indigo-electric': '#4F46E5',
        'cyan-energetic': '#06B6D4',
        'magenta-vibrant': '#EC4899',
        'gray-graphite': '#1F2937',
        'white-cloud': '#F9FAFB',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        display: ['Nunito', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
