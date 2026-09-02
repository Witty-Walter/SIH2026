import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        marine: {
          navy: "#121212", /* Deep dark neutral grey/black */
          teal: "#3F3F46", /* Zinc 700 for secondary borders/surfaces */
          safe: "#3FA66E",
          caution: "#E08A2C",
          danger: "#D93838",
          offwhite: "#F4F7F5"
        }
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
};
export default config;
