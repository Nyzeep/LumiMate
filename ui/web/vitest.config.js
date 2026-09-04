import { fileURLToPath } from "node:url";
import { defineConfig } from "vitest/config";
import vue from "@vitejs/plugin-vue";

const rootDir = fileURLToPath(new URL("./", import.meta.url));

export default defineConfig({
  root: rootDir,
  plugins: [vue()],
  test: {
    environment: "jsdom",
    include: ["src/**/*.spec.js"]
  }
});
