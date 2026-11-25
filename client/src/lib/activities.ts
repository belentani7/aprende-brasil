import type { Activity } from "./types";

/**
 * Correção das atividades — tudo determinístico e local.
 *
 * Nada aqui depende da rede: a atividade é resolvida no navegador, com o
 * gabarito que veio no currículo. Isso permite estudar offline e garante que a
 * correção não depende de um backend no ar.
 */

export type ActivityKind = Activity["kind"];

/** Normaliza texto para comparação: caixa, acentos, pontuação e espaço. */
export function normalizeAnswer(value: string): string {
  return value
    .trim()
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^\p{L}\p{N}\s]/gu, "")
    .replace(/\s+/g, " ")
    .trim();
}

export function isAnswerAccepted(activity: Activity, input: string): boolean {
  if (activity.kind !== "fill-blank") return false;
  const value = normalizeAnswer(input);
  if (!value) return false;
  return activity.acceptedAnswers.some(
    answer => normalizeAnswer(answer) === value
  );
}

export function isNumericCorrect(activity: Activity, input: number): boolean {
  if (activity.kind !== "numeric") return false;
  if (!Number.isFinite(input)) return false;
  return Math.abs(input - activity.answer) <= activity.tolerance + 1e-9;
}

/** Converte "7,5" / "R$ 7,50" / "1.250,30" em número. */
export function parseNumberInput(raw: string): number {
  const cleaned = raw
    .replace(/[^\d,.-]/g, "")
    .replace(/\.(?=\d{3}\b)/g, "")
    .replace(",", ".");
  return Number.parseFloat(cleaned);
}

export function isOrderCorrect(activity: Activity, order: number[]): boolean {
  if (activity.kind !== "ordering") return false;
  return (
    order.length === activity.correctOrder.length &&
    order.every((value, index) => value === activity.correctOrder[index])
  );
}

export function isMatchingCorrect(
  activity: Activity,
  assignment: Record<number, number>
): boolean {
  if (activity.kind !== "matching") return false;
  return activity.pairs.every((_, index) => assignment[index] === index);
}

export type ActivityResult = {
  correct: boolean;
  /** Mensagem sempre pedagógica: acerto não vira aplauso vazio. */
  feedback: string;
};

function explanationOf(activity: Activity): string {
  return "explanation" in activity && activity.explanation
    ? activity.explanation
    : "";
}

export function resultFor(
  activity: Activity,
  correct: boolean
): ActivityResult {
  const explanation = explanationOf(activity);
  if (correct) {
    return {
      correct,
      feedback: explanation
        ? `Certo. ${explanation}`
        : "Certo. Refaça sem olhar para fixar o raciocínio.",
    };
  }
  return {
    correct,
    feedback: explanation
      ? `Ainda não. ${explanation}`
      : "Ainda não. Releia a etapa e tente outra vez — errar aqui não conta como nota.",
  };
}

export function evaluateChoice(
  activity: Activity,
  index: number
): ActivityResult {
  if (activity.kind === "multiple-choice") {
    return resultFor(activity, index === activity.correctIndex);
  }
  if (activity.kind === "true-false") {
    return resultFor(activity, index === (activity.answer ? 1 : 0));
  }
  return resultFor(activity, false);
}

/** Embaralhamento determinístico: mesma ordem entre servidor e testes. */
export function shuffleStable<T>(items: T[], seed: string): T[] {
  let hash = 2166136261;
  for (let i = 0; i < seed.length; i++) {
    hash ^= seed.charCodeAt(i);
    hash = Math.imul(hash, 16777619);
  }
  const result = [...items];
  for (let i = result.length - 1; i > 0; i--) {
    hash = Math.imul(hash ^ (hash >>> 15), 2246822507);
    const j = Math.abs(hash) % (i + 1);
    [result[i], result[j]] = [result[j], result[i]];
  }
  return result;
}

export const ACTIVITY_LABEL: Record<ActivityKind, string> = {
  "multiple-choice": "Escolha uma resposta",
  "true-false": "Verdadeiro ou falso",
  "fill-blank": "Complete a lacuna",
  ordering: "Coloque em ordem",
  matching: "Ligue os pares",
  numeric: "Resposta numérica",
};
