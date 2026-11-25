#!/usr/bin/env node
/**
 * Executa um comando Python com o interpretador disponível, nesta ordem:
 * $PYTHON, .venv/bin/python, python3, python.
 *
 * Existe para que `npm run test:py` funcione tanto em ambientes ativados
 * quanto logo após criar o .venv, sem depender de `source .venv/bin/activate`.
 */
import { spawnSync } from "node:child_process";

const candidates = [
  process.env.PYTHON,
  ".venv/bin/python",
  ".venv/Scripts/python.exe",
  "python3",
  "python",
].filter(Boolean);

const args = process.argv.slice(2);
if (!args.length) {
  console.error("Uso: node scripts/run-python.mjs <comando python> [args...]");
  process.exit(2);
}

for (const candidate of candidates) {
  const probe = spawnSync(candidate, ["--version"], { stdio: "ignore" });
  if (probe.status === 0) {
    const run = spawnSync(candidate, args, { stdio: "inherit" });
    process.exit(run.status ?? 1);
  }
}

console.error(
  "Python 3 não encontrado. Crie o ambiente: python3 -m venv .venv && " +
    ".venv/bin/pip install -r requirements-dev.txt"
);
process.exit(1);
