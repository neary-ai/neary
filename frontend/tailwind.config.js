const bgPatterns = require('tailwindcss-bg-patterns');

module.exports = {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        'nunito': ['Nunito', 'sans-serif'],
        'mulish': ['Mulish', 'sans-serif'],
      },
      colors: {
        field: {
          "label": "#9EACBD",
          "divide": "#212F3A",
          "default": "#15222E",
          "focused": "#313d4b",
          "active": "#1D3345",
          "default-foreground": "#BBC7D5",
          "focused-foreground": "#ACB9C9",
          "active-foreground": "#CBD5E1"
        },
        nearyblue: {
          50: '#1D3345',
          100: '#0B1F2E',
          200: '#061725',
          300: '#03111C',
          400: '#010B13',
          500: '#00060A',
          600: '#000204',
        },
        base: {
          "50": "#e7e9ea",
          "100": "#ced2d5",
          "200": "#9da5ab",
          "300": "#6d7982",
          "400": "#3c4c58",
          "500": "#0b1f2e",
          "600": "#091925",
          "700": "#07131c",
          "800": "#040c12",
          "900": "#020609"
        },
        neutral: {
          "50": "#313d4b",
          "100": "#22303C",
          "200": "#212F3A",
          "300": "#1F2D39",
          "400": "#1A2733",
          "500": "#15222E",
        },
        nearygray: {
          50: '#CBD5E1',
          100: '#BBC7D5',
          200: '#ACB9C9',
          300: '#9EACBD',
          400: '#909EB1',
          500: '#8291A5',
          600: '#758599',
          700: '#69788D',
          800: '#5D6C81',
          900: '#526075',
        },
        nearycyan: {
          100: '#99FFFD',
          200: '#5EE6E4',
          300: '#3DCECB',
          400: '#23B5B2',
          500: '#149D9A',
        },
        nearyyellow: {
          100: '#FFDB00',
          200: '#F9C400',
        },
        nearypink: {
          100: '#FD5A8B',
          200: '#F54A7E',
          300: '#DE3E6E',
        },
        nearylight: {
          50: '#F2F5F7',
          100: '#CFDBE5',
          200: '#AFC3D3',
          300: '#90ABC2',
          400: '#7596B0',
          500: '#5F829E',
          600: '#4C6F8C',
          700: '#3D5F7A',
          800: '#315069',
          900: '#274157',
        }
      }
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
    require('@tailwindcss/forms'),
    bgPatterns,
  ],
}