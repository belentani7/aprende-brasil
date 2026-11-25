import { describe, expect, it } from "vitest";
import { KEYS, readStore, writeStore } from "./progress";
import {
  exportProgress,
  importProgress,
  resetProgress,
  sanitizeAttempts,
  sanitizeCompleted,
  sanitizeFavorites,
  sanitizeProgress,
  sanitizeReviews,
} from "./progress";

const VALID_IDS = new Set(["alfa-letra-a", "mat-soma"]);

describe("leitura tolerante do armazenamento", () => {
  it("dado corrompido não derruba a leitura", () => {
    window.localStorage.setItem(KEYS.progress, "{não é json");
    expect(readStore(KEYS.progress, {})).toEqual({});
  });

  it("grava e lê de volta", () => {
    writeStore("teste", { a: 1 });
    expect(readStore("teste", {})).toEqual({ a: 1 });
  });

  it("saneia progresso inválido", () => {
    expect(sanitizeProgress({ a: 50, b: "x", c: -10, d: 250 })).toEqual({
      a: 50,
      c: 0,
      d: 100,
    });
    expect(sanitizeProgress(null)).toEqual({});
  });

  it("saneia etapas concluídas (inteiros 1..50)", () => {
    // Números válidos passam (até de string, que o JSON antigo podia gravar);
    // fração, zero, negativo e fora do intervalo são descartados.
    expect(sanitizeCompleted({ m: [1, 1, 2, 0, -3, 99, 3.5, "4"] })).toEqual({
      m: [1, 2, 4],
    });
  });

  it("saneia favoritos (strings únicas)", () => {
    expect(sanitizeFavorites(["a", "a", 3, null, "b"])).toEqual(["a", "b"]);
    expect(sanitizeFavorites("nada")).toEqual([]);
  });

  it("saneia tentativas e limita o histórico", () => {
    const raw = [
      { moduleId: "a", activityId: "x", correct: true, at: 1 },
      { moduleId: "a", activityId: "y", correct: "sim" },
    ];
    expect(sanitizeAttempts(raw)).toEqual([
      { moduleId: "a", activityId: "x", correct: true, at: 1 },
    ]);
  });

  it("saneia revisões descartando estados inválidos", () => {
    expect(
      sanitizeReviews({
        ok: { repetitions: 1, intervalDays: 1, ease: 2.5, dueAt: 0 },
        ruim: { repetitions: "muitas" },
      })
    ).toEqual({ ok: { repetitions: 1, intervalDays: 1, ease: 2.5, dueAt: 0 } });
  });
});

describe("exportação e importação", () => {
  it("exporta o estado atual com versão", () => {
    writeStore(KEYS.progress, { "mat-soma": 40 });
    writeStore(KEYS.favorites, ["mat-soma"]);
    const snapshot = exportProgress();
    expect(snapshot.version).toBe(1);
    expect(snapshot.progress["mat-soma"]).toBe(40);
    expect(snapshot.favorites).toEqual(["mat-soma"]);
    expect(() => new Date(snapshot.exported_at).toISOString()).not.toThrow();
  });

  it("importação soma e nunca reduz progresso", () => {
    writeStore(KEYS.progress, { "mat-soma": 90 });
    const result = importProgress(
      {
        version: 1,
        progress: { "mat-soma": 20, "alfa-letra-a": 30 },
        completed: { "alfa-letra-a": [1, 2] },
        favorites: ["alfa-letra-a"],
      },
      { validIds: VALID_IDS }
    );
    expect(result.ok).toBe(true);
    expect(result.modules).toBe(2);
    expect(result.favorites).toBe(1);
    const stored = readStore<Record<string, number>>(KEYS.progress, {});
    expect(stored["mat-soma"]).toBe(90);
    expect(stored["alfa-letra-a"]).toBe(30);
    expect(readStore<string[]>(KEYS.favorites, [])).toEqual(["alfa-letra-a"]);
  });

  it("replace sobrescreve o que existia", () => {
    writeStore(KEYS.progress, { "mat-soma": 90 });
    importProgress(
      { version: 1, progress: { "alfa-letra-a": 10 } },
      { validIds: VALID_IDS, replace: true }
    );
    expect(readStore<Record<string, number>>(KEYS.progress, {})).toEqual({
      "alfa-letra-a": 10,
    });
  });

  it("ignora módulos que não existem no currículo", () => {
    const result = importProgress(
      {
        version: 1,
        progress: { inexistente: 100, "mat-soma": 10 },
        favorites: ["outro-inexistente"],
      },
      { validIds: VALID_IDS }
    );
    expect(result.modules).toBe(1);
    expect(result.ignored).toContain("inexistente");
    expect(result.favorites).toBe(0);
    expect(readStore<Record<string, number>>(KEYS.progress, {})).toEqual({
      "mat-soma": 10,
    });
  });

  it("recusa arquivo de versão desconhecida ou inválido", () => {
    expect(importProgress({ version: 9 }, { validIds: VALID_IDS }).ok).toBe(
      false
    );
    expect(importProgress("texto", { validIds: VALID_IDS }).ok).toBe(false);
    expect(importProgress(null, { validIds: VALID_IDS }).ok).toBe(false);
  });

  it("ida e volta preserva o estado", () => {
    writeStore(KEYS.progress, { "mat-soma": 55 });
    writeStore(KEYS.steps, { "mat-soma": [1, 2, 3] });
    writeStore(KEYS.favorites, ["mat-soma"]);
    const snapshot = exportProgress();

    resetProgress();
    expect(readStore(KEYS.progress, {})).toEqual({});

    importProgress(snapshot, { validIds: VALID_IDS });
    expect(readStore<Record<string, number>>(KEYS.progress, {})).toEqual({
      "mat-soma": 55,
    });
    expect(readStore(KEYS.steps, {})).toEqual({ "mat-soma": [1, 2, 3] });
    expect(readStore(KEYS.favorites, [])).toEqual(["mat-soma"]);
  });

  it("reset limpa todas as chaves de aprendizagem", () => {
    for (const key of Object.values(KEYS)) {
      if (key === KEYS.exportedAt) continue;
      writeStore(key, { a: 1 });
    }
    resetProgress();
    expect(readStore(KEYS.progress, null)).toEqual({});
    expect(readStore(KEYS.steps, null)).toEqual({});
    expect(readStore(KEYS.favorites, null)).toEqual([]);
    expect(readStore(KEYS.activity, null)).toEqual({});
    expect(readStore(KEYS.attempts, null)).toEqual([]);
    expect(readStore(KEYS.reviews, null)).toEqual({});
  });
});
