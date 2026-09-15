import { copyFileSync, existsSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const dist = resolve(root, "dist", "public");
const index = resolve(dist, "index.html");

if (!existsSync(index)) {
  console.error("postbuild: dist/public/index.html não encontrado");
  process.exit(1);
}

// GitHub Pages serve 404.html como fallback de SPA (rewrites não existem lá).
copyFileSync(index, resolve(dist, "404.html"));
console.log("postbuild: 404.html gerado para GitHub Pages");
