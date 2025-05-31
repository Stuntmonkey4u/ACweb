/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'wotlk-blue': '#1A3A5A',
        'wotlk-light-blue': '#60A5FA',
        'wotlk-gold': '#FFD700',
        'wotlk-parchment': '#F5E8C7',
        'wotlk-parchment-dark': '#EADCB8',
        'wotlk-stone': '#4A5568', // Gray-700
        'wotlk-dark-stone': '#2D3748', // Gray-800
        'wotlk-ice': '#E0FFFF',
        'wotlk-text-dark': '#1A202C', // Gray-900
        'wotlk-text-light': '#E2E8F0', // Gray-200
      },
      fontFamily: {
        'cinzel': ['Cinzel', 'serif'], // For headings, WotLK feel
        'sans': ['Roboto', 'system-ui', 'sans-serif'], // Default sans-serif for body
      },
      backgroundImage: {
        // Example: 'parchment-texture': "url('/path/to/parchment-texture.png')",
      },
      borderColor: theme => ({
        ...theme('colors'),
        DEFAULT: theme('colors.gray.300', 'currentColor'),
        'wotlk-gold': '#FFD700',
        'wotlk-stone': '#4A5568',
      }),
      boxShadow: {
        'stone': 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.2), 0 2px 10px 0 rgba(0, 0, 0, 0.1)',
        'input-inset': 'inset 0 2px 4px 0 rgba(0,0,0,0.1)',
      }
    },
  },
  plugins: [],
}
