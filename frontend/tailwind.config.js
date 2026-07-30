/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        background: 'var(--background)',
        foreground: 'var(--foreground)',
        primary: {
          DEFAULT: '#1E293B',
          foreground: '#F8FAFC',
        },
        accent: {
          DEFAULT: '#0F766E',
          foreground: '#F0FDFA',
        },
        verified: {
          DEFAULT: '#166534',
          bg: '#DCFCE7',
        },
        pending: {
          DEFAULT: '#854D0E',
          bg: '#FEF9C3',
        }
      },
    },
  },
  plugins: [],
}
