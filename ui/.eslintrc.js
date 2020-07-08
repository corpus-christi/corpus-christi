module.exports = {
  root: true,

  env: {
    node: true,
  },

  extends: ["plugin:vue/essential", "@vue/prettier"],

  rules: {
    // FIXME: Restore this setting after chasing out console calls.
    // "no-console": process.env.NODE_ENV === "production" ? "error" : "off",
    "no-console": "off",
    "no-debugger": process.env.NODE_ENV === "production" ? "error" : "off",
  },

  extends: ["plugin:vue/essential", "@vue/prettier"],
};
