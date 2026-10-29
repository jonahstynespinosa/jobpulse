/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./index.html'],
  theme: {
    extend: {
      colors: {
        jp: {
          bg:      '#0f1117',
          surface: '#1a1d27',
          border:  '#2a2d3a',
          accent:  '#6366f1',
          hover:   '#818cf8',
          text:    '#e2e8f0',
          muted:   '#8b93a7',
          tag:     '#1e2035',
        },
      },
      borderRadius: {
        card: '10px',
      },
    },
  },
  plugins: [],
}
