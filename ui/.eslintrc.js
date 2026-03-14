module.exports = {
  root: true,

  env: {
    node: true,
    browser: true
  },

  extends: [
    "plugin:vue/vue3-recommended",
    "@vue/eslint-config-typescript",
    "@vue/eslint-config-prettier"
  ],

  rules: {
    "no-console": "off",
    "no-debugger": process.env.NODE_ENV === "production" ? "error" : "off",
    "vue/multi-word-component-names": "off"
  },

  parserOptions: {
    ecmaVersion: "latest"
  }
};
