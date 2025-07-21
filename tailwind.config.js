/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./orders/templates/**/*.html",
    "./vendors/templates/**/*.html",
    "./static/**/*.js",
    "./assets/**/*.js",
    "./core/**/*.py",
    "./orders/**/*.py",
    "./vendors/**/*.py",
  ],
  theme: {
    extend: {},
  },
  plugins: [require("daisyui")],
  daisyui: {
    themes: ["dark", "light", "cupcake", "cyberpunk"],
    darkTheme: "dark",
    base: true,
    styled: true,
    utils: true,
    prefix: "",
    logs: true,
    themeRoot: ":root",
  },
};
