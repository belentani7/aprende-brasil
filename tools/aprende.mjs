#!/usr/bin/env node
/**
 * CLI interna da Aprende Brasil.
 *
 * Uso:
 *   node tools/aprende.mjs stats       # números do currículo exportado
 *   node tools/aprende.mjs validate    # contrato dos dados (sai 1 se falhar)
 *   node tools/aprende.mjs budget      # orçamento do build em dist/public
 *   node tools/aprende.mjs --help
 *
 * Sem dependências: apenas Node 22+ (fs, path, zlib).
 */
import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { dirname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { gzipSync } from "node:zlib";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const CATALOG = join(ROOT, "client", "src", "data", "curriculum.json");
const STEPS = join(ROOT, "client", "src", "data", "curriculum-steps.json");
const DIST = join(ROOT, "dist", "public");
const STEP_TYPES = ["explanation", "example", "practice", "check", "next"];

/** Orçamento em KiB (gzip) — falha o comando se estourar. */
const BUDGET = {
  initialJsKb: 120,
  cssKb: 15,
  totalKb: 1536,
};

const PLACEHOLDERS = [
  "Exemplo prático sobre",
  "Ótimo! Continue praticando",
  "Veja este exemplo de",
  "Vamos aprender a",
  "Pratique com um exemplo real",
];

function readJson(path) {
  if (!existsSync(path)) {
    throw new Error(
      `Arquivo ausente: ${relative(ROOT, path)}. Rode "npm run curriculum".`
    );
  }
  return JSON.parse(readFileSync(path, "utf8"));
}

function loadData() {
  const catalog = readJson(CATALOG);
  const steps = readJson(STEPS);
  return { catalog, steps };
}

function fmt(bytes) {
  return `${(bytes / 1024).toFixed(1)} KiB`;
}

function table(rows) {
  const width = Math.max(...rows.map(row => row[0].length));
  return rows
    .map(([label, value]) => `  ${label.padEnd(width)}  ${value}`)
    .join("\n");
}

function walk(dir) {
  if (!existsSync(dir)) return [];
  return readdirSync(dir, { withFileTypes: true }).flatMap(entry => {
    const full = join(dir, entry.name);
    return entry.isDirectory() ? walk(full) : [full];
  });
}

function gzipSize(path) {
  return gzipSync(readFileSync(path)).length;
}

const commands = {
  stats() {
    const { catalog, steps } = loadData();
    const modules = catalog.modules;
    const perTrack = new Map();
    for (const module of modules) {
      perTrack.set(module.track_id, (perTrack.get(module.track_id) ?? 0) + 1);
    }
    const totalSteps = Object.values(steps).reduce(
      (sum, list) => sum + list.length,
      0
    );
    const perType = new Map();
    for (const list of Object.values(steps)) {
      for (const step of list)
        perType.set(step.type, (perType.get(step.type) ?? 0) + 1);
    }

    console.log("Currículo exportado\n");
    console.log(
      table([
        ["Trilhas", String(catalog.tracks.length)],
        ["Módulos", String(modules.length)],
        ["Etapas", String(totalSteps)],
        ["Catálogo", fmt(statSync(CATALOG).size)],
        ["Etapas (arquivo)", fmt(statSync(STEPS).size)],
      ])
    );
    console.log("\nPor trilha\n");
    console.log(
      table(
        catalog.tracks.map(track => [
          track.label,
          `${perTrack.get(track.id) ?? 0} módulos`,
        ])
      )
    );
    console.log("\nPor tipo de etapa\n");
    console.log(
      table(STEP_TYPES.map(type => [type, String(perType.get(type) ?? 0)]))
    );
    return 0;
  },

  validate() {
    const { catalog, steps } = loadData();
    const errors = [];

    if (catalog.tracks.length !== 4)
      errors.push(`esperadas 4 trilhas, encontradas ${catalog.tracks.length}`);
    if (catalog.modules.length !== 205)
      errors.push(
        `esperados 205 módulos, encontrados ${catalog.modules.length}`
      );

    const trackIds = new Set(catalog.tracks.map(t => t.id));
    const moduleIds = new Set();
    let totalSteps = 0;

    for (const module of catalog.modules) {
      if (moduleIds.has(module.id)) errors.push(`id duplicado: ${module.id}`);
      moduleIds.add(module.id);
      if (!trackIds.has(module.track_id))
        errors.push(`${module.id}: trilha inexistente "${module.track_id}"`);
      if (!module.title?.trim()) errors.push(`${module.id}: título vazio`);
      if (module.step_count !== 5)
        errors.push(`${module.id}: step_count=${module.step_count}`);

      const list = steps[module.id];
      if (!Array.isArray(list)) {
        errors.push(`${module.id}: sem etapas exportadas`);
        continue;
      }
      totalSteps += list.length;
      const orders = list.map(step => step.order);
      if (orders.join(",") !== "1,2,3,4,5")
        errors.push(`${module.id}: ordem das etapas ${orders.join(",")}`);
      const types = list.map(step => step.type);
      if (types.join(",") !== STEP_TYPES.join(","))
        errors.push(`${module.id}: tipos ${types.join(",")}`);
      for (const step of list) {
        const text = step.content?.text?.trim() ?? "";
        if (text.length < 20)
          errors.push(`${module.id}/${step.order}: texto curto`);
        for (const marca of PLACEHOLDERS) {
          if (text.includes(marca))
            errors.push(`${module.id}/${step.order}: placeholder "${marca}"`);
        }
      }
    }

    for (const track of catalog.tracks) {
      const count = catalog.modules.filter(m => m.track_id === track.id).length;
      if (count !== track.module_count) {
        errors.push(
          `${track.id}: module_count=${track.module_count}, real=${count}`
        );
      }
    }

    const orphanSteps = Object.keys(steps).filter(id => !moduleIds.has(id));
    if (orphanSteps.length)
      errors.push(`etapas de módulos inexistentes: ${orphanSteps.join(", ")}`);
    if (totalSteps !== 1025)
      errors.push(`esperadas 1025 etapas, encontradas ${totalSteps}`);

    if (errors.length) {
      console.error(`Falha na validação (${errors.length} problema(s)):\n`);
      for (const error of errors.slice(0, 40)) console.error(`  ✗ ${error}`);
      if (errors.length > 40) console.error(`  … e mais ${errors.length - 40}`);
      return 1;
    }

    console.log(
      `✓ Currículo válido: ${catalog.tracks.length} trilhas, ` +
        `${moduleIds.size} módulos, ${totalSteps} etapas em 5 passos cada.`
    );
    return 0;
  },

  budget() {
    if (!existsSync(join(DIST, "index.html"))) {
      console.error('Build ausente. Rode "npm run build" antes do orçamento.');
      return 1;
    }

    const html = readFileSync(join(DIST, "index.html"), "utf8");
    const initialJs = [...html.matchAll(/<script[^>]+src="([^"]+\.js)"/g)].map(
      m => m[1]
    );
    const css = [...html.matchAll(/<link[^>]+href="([^"]+\.css)"/g)].map(
      m => m[1]
    );

    const files = walk(DIST);
    const totalBytes = files.reduce(
      (sum, file) => sum + statSync(file).size,
      0
    );
    const rows = [];
    let failed = false;

    const jsGzip = initialJs.reduce(
      (sum, src) => sum + gzipSize(join(DIST, src.replace(/^\//, ""))),
      0
    );
    const cssGzip = css.reduce(
      (sum, href) => sum + gzipSize(join(DIST, href.replace(/^\//, ""))),
      0
    );

    const check = (label, valueKb, limitKb, unit = "gzip") => {
      const ok = valueKb <= limitKb;
      if (!ok) failed = true;
      rows.push([
        label,
        `${valueKb.toFixed(1)} KiB ${unit} / limite ${limitKb} KiB ${ok ? "✓" : "✗"}`,
      ]);
    };

    check("JS inicial", jsGzip / 1024, BUDGET.initialJsKb);
    check("CSS", cssGzip / 1024, BUDGET.cssKb);
    check("Build total", totalBytes / 1024, BUDGET.totalKb, "em disco");
    rows.push(["Arquivos", String(files.length)]);
    rows.push([
      "Chunks JS",
      String(files.filter(f => f.endsWith(".js")).length),
    ]);

    console.log("Orçamento de build (dist/public)\n");
    console.log(table(rows));

    if (failed) {
      console.error(
        "\n✗ Orçamento estourado: reduza o custo ou justifique o aumento em tools/aprende.mjs."
      );
      return 1;
    }
    console.log("\n✓ Orçamento respeitado.");
    return 0;
  },
};

function help() {
  console.log(`aprende. CLI interna

Uso:
  node tools/aprende.mjs <comando>

Comandos:
  stats      Mostra trilhas, módulos, etapas e tamanho dos dados.
  validate   Verifica o contrato do currículo (ids, 5 etapas, textos, trilhas).
  budget     Mede o build em dist/public e compara com o orçamento.
  --help     Esta ajuda.

Exemplos:
  npm run stats
  npm run audit
  node tools/aprende.mjs budget

Sai com código 1 quando um contrato ou orçamento falha — pronto para CI.`);
  return 0;
}

const command = process.argv[2] ?? "--help";
if (command === "--help" || command === "-h" || command === "help") {
  process.exit(help());
}

if (!commands[command]) {
  console.error(`Comando desconhecido: ${command}\n`);
  help();
  process.exit(1);
}

try {
  process.exit(commands[command]());
} catch (error) {
  console.error(
    `Erro: ${error instanceof Error ? error.message : String(error)}`
  );
  process.exit(1);
}
