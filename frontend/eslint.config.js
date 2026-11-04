import js from "@eslint/js";
import globals from "globals";

export default [
  {ignores: ["node_modules/**"]},
  js.configs.recommended,
  {
    files: ["**/*.js"],
    languageOptions: {globals: {...globals.browser, ...globals.node}},
    rules: {"no-unused-vars": ["error", {argsIgnorePattern: "^_", caughtErrors: "none"}]},
  },
];
