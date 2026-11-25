import { defineConfig, devices } from "@playwright/test";

/**
 * E2E contra o build real servido por `vite preview`.
 *
 * - O preview roda em 127.0.0.1:4173 com o próprio build (nada de dev server).
 * - `baseURL` inclui o subpath quando `VITE_BASE_PATH` é usado, então o mesmo
 *   teste serve para raiz ("/") e para GitHub Pages ("/aprende-brasil/").
 * - Chromium é o único navegador; `desktop` roda tudo e `mobile` roda só os
 *   testes marcados com `@mobile` (layout de celular barato, o nosso público).
 */
const basePath = process.env.VITE_BASE_PATH || "/";
const baseURL = `http://127.0.0.1:4173${basePath.replace(/\/$/, "")}`;

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  // Duas retentativas no CI: navegador real em runner compartilhado tem ruído.
  // Se um teste só passa na terceira, ele está frágil e o relatório o marca como
  // "flaky" — na revisão isso é tratado como defeito, não como "já passou".
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 2 : undefined,
  reporter: process.env.CI ? [["list"], ["html", { open: "never" }]] : "list",
  expect: { timeout: 10_000 },
  use: {
    baseURL,
    actionTimeout: 15_000,
    navigationTimeout: 30_000,
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
