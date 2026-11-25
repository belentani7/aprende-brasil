/// <reference types="vitest/config" />
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { existsSync } from "node:fs";
import path, { join } from "node:path";
import { defineConfig, type Plugin } from "vite";

/**
 * `VITE_BASE_PATH` é o único ponto de configuração do subpath:
 *   - "/"                  → Vercel, Netlify, Cloudflare e FastAPI local
 *   - "/aprende-brasil/"   → GitHub Pages (projeto servido em subpasta)
 *
 * O router (wouter) lê `import.meta.env.BASE_URL`, então mudar aqui ajusta as
 * rotas junto com os assets — não existe caminho absoluto escrito à mão.
 */
const base = process.env.VITE_BASE_PATH || "/";

/**
 * O preview do Arena/E2B chega por um host próprio e dinâmico. Em
 * desenvolvimento/preview liberamos hosts, mas **somente** quando a variável
 * estiver definida; em produção o app é estático e não roda servidor Vite.
 */
const previewHosts = process.env.VITE_PREVIEW_ALLOWED_HOSTS;

/**
 * O `vite preview` aplica fallback de SPA em tudo: pedir `/assets/x.js`
 * inexistente devolve `index.html` com 200. O navegador então falha ao
 * executar o módulo ("MIME type text/html"), e isso esconde asset quebrado.
 *
 * Este plugin mantém o fallback para rotas de verdade (`/modulo/...`,
 * `/progresso`) e devolve 404 para qualquer caminho com extensão — o mesmo
 * comportamento do servidor FastAPI (`SPAStaticFiles`).
 */
function previewAssetGuard(): Plugin {
  return {
    name: "aprende-preview-asset-guard",
    configurePreviewServer(server) {
      server.middlewares.use((req, res, next) => {
        const url = (req.url ?? "/").split("?")[0];
        const last = url.split("/").pop() ?? "";
        if (last.includes(".") && !url.startsWith("/api/")) {
          // Só deixa passar o que realmente existe no build.
          const file = new URL(url, "http://local").pathname;
          if (!/\.(?:[a-z0-9]{1,8})$/i.test(last)) return next();
          res.setHeader("Cache-Control", "no-store");
          const onDisk = join(
            __dirname,
            "dist",
            "public",
            file.replace(/^\//, "")
          );
          if (!existsSync(onDisk)) {
            res.statusCode = 404;
            res.setHeader("Content-Type", "text/plain; charset=utf-8");
            res.end("Not found");
            return;
          }
        }
        next();
      });
    },
  };
}

export default defineConfig({
  base,
  plugins: [react(), tailwindcss(), previewAssetGuard()],
  root: "client",
  server: {
    host: "0.0.0.0",
    // Proxy para a API FastAPI em desenvolvimento, para que o navegador fale
    // apenas com a origem do Vite (sem CORS e sem localhost cruzado).
    proxy: {
      "/api": {
        target: process.env.VITE_DEV_API_TARGET || "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
  preview: {
    host: "0.0.0.0",
    port: 4173,
    // Lista explícita e opcional: sem a variável, o Vite usa o padrão seguro.
    ...(previewHosts
      ? { allowedHosts: previewHosts.split(",").map(host => host.trim()) }
      : {}),
  },
  build: {
    outDir: "../dist/public",
    emptyOutDir: true,
    // Build reprodutível: nomes de arquivo derivam do conteúdo, não do tempo.
    sourcemap: false,
    target: "es2020",
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "client/src"),
    },
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./src/test/setup.ts"],
    include: ["./src/**/*.test.{ts,tsx}"],
    restoreMocks: true,
  },
});
