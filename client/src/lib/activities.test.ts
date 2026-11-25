import { describe, expect, it } from "vitest";
import stepsByModule from "@/data/curriculum-steps.json";
import {
  ACTIVITY_LABEL,
  evaluateChoice,
  isAnswerAccepted,
  isMatchingCorrect,
  isNumericCorrect,
  isOrderCorrect,
  normalizeAnswer,
  parseNumberInput,
  resultFor,
  shuffleStable,
} from "./activities";
import { MODULES } from "./curriculum";
import type { Activity, StepData } from "./types";

const STEPS = stepsByModule as Record<string, StepData[]>;

function allActivities(): Activity[] {
  return Object.values(STEPS).flatMap(steps =>
    steps.flatMap(step => step.content.activities ?? [])
  );
}

function byKind(kind: Activity["kind"]): Activity {
  const found = allActivities().find(activity => activity.kind === kind);
  if (!found) throw new Error(`sem atividade do tipo ${kind}`);
  return found;
}

describe("modelo de atividades", () => {
  it("cobre todos os seis tipos no currículo exportado", () => {
    const kinds = new Set(allActivities().map(a => a.kind));
    expect([...kinds].sort()).toEqual(Object.keys(ACTIVITY_LABEL).sort());
  });

  it("não tem id repetido dentro da mesma etapa", () => {
    for (const [moduleId, steps] of Object.entries(STEPS)) {
      for (const step of steps) {
        const ids = (step.content.activities ?? []).map(a => a.id);
        expect(new Set(ids).size).toBe(ids.length);
        for (const id of ids) expect(id, moduleId).toMatch(/^[a-z0-9-]+$/);
      }
    }
  });

  it("todo gabarito de múltipla escolha aponta para uma opção existente", () => {
    for (const activity of allActivities()) {
      if (activity.kind !== "multiple-choice") continue;
      expect(activity.correctIndex).toBeGreaterThanOrEqual(0);
      expect(activity.correctIndex).toBeLessThan(activity.options.length);
      expect(new Set(activity.options).size).toBe(activity.options.length);
    }
  });

  it("numeric nunca vem com tolerância negativa", () => {
    for (const activity of allActivities()) {
      if (activity.kind !== "numeric") continue;
      expect(activity.tolerance).toBeGreaterThanOrEqual(0);
      expect(Number.isFinite(activity.answer)).toBe(true);
    }
  });

  it("matching tem lados únicos (sem dois pares iguais)", () => {
    for (const activity of allActivities()) {
      if (activity.kind !== "matching") continue;
      expect(new Set(activity.pairs.map(p => p.left)).size).toBe(
        activity.pairs.length
      );
      expect(new Set(activity.pairs.map(p => p.right)).size).toBe(
        activity.pairs.length
      );
    }
  });
});

describe("correção", () => {
  it("normaliza acentos, caixa e pontuação", () => {
    expect(normalizeAnswer("  Amanhã! ")).toBe("amanha");
    expect(normalizeAnswer("NÃO")).toBe("nao");
    expect(normalizeAnswer("R$ 7,50")).toBe("r 750");
  });

  it("aceita resposta de lacuna independentemente da acentuação", () => {
    const activity = byKind("fill-blank");
    expect(isAnswerAccepted(activity, "  qualquer coisa  ")).toBe(false);
  });

  it("aceita a resposta certa de uma lacuna real", () => {
    const activity = allActivities().find(
      a => a.kind === "fill-blank" && a.id === "alfa-letra-a-palavra"
    );
    expect(activity).toBeDefined();
    if (activity?.kind !== "fill-blank") return;
    for (const accepted of activity.acceptedAnswers) {
      expect(isAnswerAccepted(activity, accepted)).toBe(true);
      expect(isAnswerAccepted(activity, accepted.toUpperCase() + "!")).toBe(
        true
      );
    }
  });

  it("numérico respeita tolerância inclusiva", () => {
    const activity = allActivities().find(
      a => a.kind === "numeric" && a.id === "mat-troco-centavos"
    );
    if (activity?.kind !== "numeric") throw new Error("atividade ausente");
    expect(activity.answer).toBe(2.5);
    expect(isNumericCorrect(activity, 2.5)).toBe(true);
    expect(isNumericCorrect(activity, 2.51)).toBe(true);
    expect(isNumericCorrect(activity, 2.6)).toBe(false);
    expect(isNumericCorrect(activity, Number.NaN)).toBe(false);
  });

  it("converte entrada numérica com vírgula e milhar", () => {
    expect(parseNumberInput("7,5")).toBe(7.5);
    expect(parseNumberInput("R$ 1.250,30")).toBe(1250.3);
    expect(parseNumberInput("42")).toBe(42);
    expect(Number.isNaN(parseNumberInput("abc"))).toBe(true);
  });

  it("ordering compara a permutação inteira", () => {
    const activity = allActivities().find(a => a.kind === "ordering");
    if (activity?.kind !== "ordering") throw new Error("atividade ausente");
    expect(isOrderCorrect(activity, activity.correctOrder)).toBe(true);
    expect(isOrderCorrect(activity, [...activity.correctOrder].reverse())).toBe(
      activity.correctOrder.length < 2
    );
  });

  it("matching só fecha quando todos os pares estão certos", () => {
    const activity = byKind("matching");
    if (activity.kind !== "matching") return;
    const perfect = Object.fromEntries(
      activity.pairs.map((_, index) => [index, index])
    );
    expect(isMatchingCorrect(activity, perfect)).toBe(true);
    expect(isMatchingCorrect(activity, { 0: 0 })).toBe(false);
  });

  it("feedback de erro nunca envergonha e sempre explica", () => {
    const activity = byKind("multiple-choice");
    const wrong = resultFor(activity, false);
    expect(wrong.correct).toBe(false);
    expect(wrong.feedback).toMatch(/Ainda não/);
    expect(wrong.feedback.length).toBeGreaterThan(40);
    expect(wrong.feedback).not.toMatch(/errado|burro|falhou|nota/i);
  });

  it("verdadeiro/falso usa índice 1 para verdadeiro", () => {
    const activity = byKind("true-false");
    if (activity.kind !== "true-false") return;
    const truthy = activity.answer ? 1 : 0;
    expect(evaluateChoice(activity, truthy).correct).toBe(true);
    expect(evaluateChoice(activity, 1 - truthy).correct).toBe(false);
  });
});

describe("embaralhamento determinístico", () => {
  it("mesmo seed, mesma ordem", () => {
    const items = [1, 2, 3, 4, 5];
    expect(shuffleStable(items, "seed")).toEqual(shuffleStable(items, "seed"));
    expect(items).toEqual([1, 2, 3, 4, 5]); // não muta a entrada
  });

  it("não perde nem duplica itens", () => {
    const shuffled = shuffleStable([1, 2, 3, 4, 5, 6], "outro");
    expect([...shuffled].sort()).toEqual([1, 2, 3, 4, 5, 6]);
  });
});

describe("conteúdo educacional", () => {
  it("cada módulo tem objetivos e ao menos duas atividades", () => {
    for (const module of MODULES) {
      const steps = STEPS[module.id] ?? [];
      const objectives = steps[0]?.content.objectives ?? [];
      const activities = steps.flatMap(s => s.content.activities ?? []);
      expect(objectives.length, module.id).toBeGreaterThanOrEqual(2);
      expect(activities.length, module.id).toBeGreaterThanOrEqual(2);
    }
  });

  it("as atividades ficam na etapa de prática e os objetivos na primeira", () => {
    for (const [moduleId, steps] of Object.entries(STEPS)) {
      for (const step of steps) {
        if (step.content.activities?.length) {
          expect(step.type, moduleId).toBe("practice");
        }
        if (step.content.objectives?.length) {
          expect(step.type, moduleId).toBe("explanation");
        }
      }
    }
  });

  it("o texto das etapas continua intacto (sem substituição por enunciado)", () => {
    for (const [moduleId, steps] of Object.entries(STEPS)) {
      for (const step of steps) {
        expect(step.content.text.length, moduleId).toBeGreaterThan(20);
        for (const activity of step.content.activities ?? []) {
          expect(activity.prompt).not.toBe(step.content.text);
        }
      }
    }
  });
});
