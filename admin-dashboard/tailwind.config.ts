import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        espresso: '#241813',
        'dark-coffee': '#34251F',
        'warm-cream': '#F7F2E9',
        milk: '#FFFDF8',
        caramel: '#C58B58',
        sage: '#9AA58C',
        'muted-text': '#95877D',
      },
    },
  },
  plugins: [],
}
export default config
