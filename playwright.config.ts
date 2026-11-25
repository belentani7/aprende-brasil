import { defineConfig, devices } from "@playwright/test";

/**
 * E2E contra o build real servido por `vite preview`.
 *
 * - O preview roda em 127.0.0.1:4173 com o próprio build (nada de dev server).
 * - `baseURL` inclui o subpath quando `VITE_BASE_PATH` é usado, então o mesmo
 *   teste serve para raiz ("/") e para GitHub Pages ("/aprende-brasil/").
 * - Chromium é o único projeto por padrão (CI leve); `--project=mobile` existe
 *   para checar o layout de celular.
 */
const basePath = process.env.VITE_BASE_PATH || "/";
const baseURL = `http://127.0.0.1:4173${basePath.replace(/\/$/, "")}`;

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: process.env.CI ? 2 : undefined,
  reporter: process.env.CI ? [["list"], ["html", { open: "never" }]] : "list",
  use: {
    baseURL,
    trace: "on-first-retry",
    video: "off",
  },
  projects: [
    { name: "desktop", use: { ...devices["Desktop Chrome"] } },
    { name: "mobile", use: { ...devices["Pixel 5"] }, grep: /@mobile/ },
  ],
  webServer: {
    command: `npx vite preview --host 127.0.0.1 --port 4173`,
    url: "http://127.0.0.1:4173",
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
});
