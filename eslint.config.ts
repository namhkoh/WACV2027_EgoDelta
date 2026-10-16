import js from "@eslint/js";
import globals from "globals";
import typescript from "typescript-eslint";
import astro from "eslint-plugin-astro";
import json from "@eslint/json";
import markdown from "@eslint/markdown";
import css from "@eslint/css";
import { defineConfig, globalIgnores } from "eslint/config";

export default defineConfig([
  globalIgnores(["dist/*", ".astro/*", ".vscode/*", "package-lock.json"]),
  {
    files: ["**/*.{js,mjs,cjs,ts,mts,cts,jsx,tsx}"],
    plugins: { js },
    extends: ["js/recommended"],
    languageOptions: { globals: { ...globals.browser, ...globals.node } },
  },
  {
    files: ["**/*.{ts,tsx,mts,cts}"],
    extends: [typescript.configs.recommended],
  },
  {
    files: ["**/*.astro"],
    plugins: { astro },
    extends: [astro.configs.recommended],
  },
  {
    files: ["**/*.json"],
    plugins: { json },
    language: "json/json",
    extends: [json.configs.recommended],
  },
  {
    files: ["**/*.ts", "**/*.tsx"],
    languageOptions: {
      parser: typescript.parser,
      parserOptions: {
        // Enable project service for better TypeScript integration
        projectService: true,
        tsconfigRootDir: import.meta.dirname,
      },
    },
  },
  {
    files: ["**/*.md"],
    plugins: { markdown },
    language: "markdown/gfm",
    extends: [markdown.configs.recommended],
  },
  {
    files: ["**/*.css"],
    plugins: { css },
    language: "css/css",
    extends: [css.configs.recommended],
    rules: {
      // The font stacks reference variables that Astro's font API injects at build time.
      "css/no-invalid-properties": ["error", { allowUnknownVariables: true }],
      // text-wrap: balance and :has() are progressive enhancements here.
      "css/use-baseline": ["error", { available: "newly" }],
    },
  },
]);
