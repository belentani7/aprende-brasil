#!/usr/bin/env node
/**
 * Gera o currículo estático a partir de data/aprende.db usando só a stdlib do
 * Python 3. Em hosts de build que têm apenas Node (ou onde /data e /scripts são
 * excluídos do deploy), usa os JSON já versionados — e falha se eles não
 * existirem.
 *
 * Uso:
 *   node scripts/build-curriculum.mjs           # gera (ou reutiliza)
 *   node scripts/build-curriculum.mjs --check   # falha se o JSON estiver dessincronizado
 */
import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const python = process.env.PYTHON ?? "python3";
const exporter = resolve(root, "scripts", "export_static_curriculum.py");
const database = resolve(root, "data", "aprende.db");
const outputs = [
  resolve(root, "client", "src", "data", "curriculum.json"),
  resolve(root, "client", "src", "data", "curriculum-steps.json"),
];
const check = process.argv.includes("--check");

if (!existsSync(database) && outputs.every(existsSync) && !check) {
  console.log(
    "curriculum: data/aprende.db indisponível neste ambiente; usando os JSON versionados."
  );
  process.exit(0);
}

const result = spawnSync(python, [exporter, ...(check ? ["--check"] : [])], {
  cwd: root,
  stdio: "inherit",
});

if (result.error?.code === "ENOENT") {
  console.error(
    `curriculum: Python 3 não encontrado (${python}). ` +
      "Instale python3 ou rode o build em um ambiente com o banco disponível."
  );
  process.exit(1);
}

process.exit(result.status ?? 1);
