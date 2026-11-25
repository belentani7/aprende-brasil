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
// O arquivo precisa usar o mesmo base das rotas para a navegação profunda
// funcionar em /aprende-brasil/modulo/...
copyFileSync(index, resolve(dist, "404.html"));

// Open Data é servido como arquivo estático. Garantir o .nojekyll evita que o
// Pages ignore pastas que começam com "_" (comportamento do Jekyll).
copyFileSync(resolve(root, "client", "public", ".nojekyll"), resolve(dist, ".nojekyll"));

const base = process.env.VITE_BASE_PATH || "/";
console.log(
  `postbuild: 404.html e .nojekyll gerados (base "${base}") para GitHub Pages`
);
