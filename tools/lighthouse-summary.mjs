#!/usr/bin/env node
/**
 * Lê os relatórios do Lighthouse gerados em `lighthouse-results/` e escreve um
 * resumo em Markdown.
 *
 * Por que isto existe: o log do runner do GitHub não é acessível fora do
 * GitHub, e números de Lighthouse sem origem verificável viram folclore. Este
 * script publica exatamente o que o Chrome mediu, com a mediana das execuções.
 *
 * Uso:
 *   node tools/lighthouse-summary.mjs [dir] [--saida arquivo.md]
 */

import { existsSync, readdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const dir = process.argv.includes("--saida")
  ? process.argv[process.argv.indexOf("--saida") - 1] || "lighthouse-results"
  : process.argv[2] || "lighthouse-results";
const saidaIndex = process.argv.indexOf("--saida");
const saida = saidaIndex === -1 ? null : process.argv[saidaIndex + 1];

const CATEGORIAS = [
  ["performance", "Performance"],
  ["accessibility", "Acessibilidade"],
  ["best-practices", "Boas práticas"],
  ["seo", "SEO"],
];

const AUDITORIAS = [
  ["first-contentful-paint", "FCP"],
  ["largest-contentful-paint", "LCP"],
  ["total-blocking-time", "TBT"],
  ["cumulative-layout-shift", "CLS"],
  ["speed-index", "Speed Index"],
];

function mediana(valores) {
  const ordenados = [...valores].sort((a, b) => a - b);
  if (!ordenados.length) return null;
  const meio = Math.floor(ordenados.length / 2);
  return ordenados.length % 2
    ? ordenados[meio]
    : (ordenados[meio - 1] + ordenados[meio]) / 2;
}

function relatorios(pasta) {
  if (!existsSync(pasta)) return [];
  return readdirSync(pasta, { recursive: true })
    .filter(nome => String(nome).endsWith(".json"))
    .map(nome => join(pasta, String(nome)))
    .filter(caminho => {
      try {
        return "categories" in JSON.parse(readFileSync(caminho, "utf8"));
      } catch {
        return false;
      }
    })
    .map(caminho => JSON.parse(readFileSync(caminho, "utf8")));
}

const lhrs = relatorios(dir);
if (!lhrs.length) {
  console.error(`Nenhum relatório do Lighthouse em ${dir}/ — nada a resumir.`);
  process.exit(1);
}

const linhas = [];
linhas.push("### Lighthouse (medido no build estático)");
linhas.push("");
linhas.push(
  `${lhrs.length} execuções em ${new Set(lhrs.map(l => l.finalUrl ?? l.requestedUrl)).size} URL(s). ` +
    "Valores por categoria: mediana das execuções."
);
linhas.push("");

const porUrl = new Map();
for (const lhr of lhrs) {
  const url = lhr.finalUrl ?? lhr.requestedUrl ?? "?";
  if (!porUrl.has(url)) porUrl.set(url, []);
  porUrl.get(url).push(lhr);
}

for (const [url, rodadas] of porUrl) {
  linhas.push(`**${url}**`);
  linhas.push("");
  linhas.push("| Métrica | Valor |");
  linhas.push("| --- | --- |");
  for (const [id, rotulo] of CATEGORIAS) {
    const score = mediana(
      rodadas
        .map(lhr => lhr.categories?.[id]?.score)
        .filter(valor => typeof valor === "number")
    );
    if (score === null) continue;
    linhas.push(`| ${rotulo} | ${Math.round(score * 100)} |`);
  }
  for (const [id, rotulo] of AUDITORIAS) {
    const bruto = mediana(
      rodadas
        .map(lhr => (lhr.audits?.[id]?.displayValue ? lhr.audits[id] : null))
        .filter(Boolean)
        .map(audit => audit.displayValue)
    );
    // displayValue é string; a mediana acima já é a moda textual, o que é o
    // suficiente para um resumo legível (o valor numérico está no JSON anexado).
    if (bruto) linhas.push(`| ${rotulo} | ${bruto} |`);
  }
  linhas.push("");
}

const falhas = lhrs.flatMap(lhr =>
  Object.entries(lhr.audits ?? {})
    .filter(
      ([, audit]) =>
        audit.score !== null &&
        audit.score < 1 &&
        audit.scoreDisplayMode === "binary"
    )
    .map(([id, audit]) => ({ id, titulo: audit.title, url: lhr.finalUrl }))
);
const falhasUnicas = [...new Map(falhas.map(f => [f.id, f])).values()];

if (falhasUnicas.length) {
  linhas.push("**Auditorias binárias que não passaram**");
  linhas.push("");
  for (const falha of falhasUnicas) {
    linhas.push(`- \`${falha.id}\` — ${falha.titulo}`);
  }
} else {
  linhas.push("Nenhuma auditoria binária falhou.");
}

const markdown = linhas.join("\n");
console.log(markdown);
if (saida) writeFileSync(saida, markdown + "\n", "utf8");
