/**
 * Revisão espaçada (SM-2 simplificado) e leitura de evidências.
 *
 * Duas ideias separadas, de propósito:
 *
 * - **Progresso** é o que a pessoa fez (páginas lidas, etapas marcadas).
 * - **Domínio** é o que ela demonstrou saber (acertos nas atividades e revisões).
 *
 * Completar uma página não prova domínio. Por isso a recomendação de revisão
 * olha para os acertos, não para o percentual da barra.
 *
 * Nada aqui pune: a qualidade baixa só encurta o intervalo de volta. Não existe
 * nota, ranking nem comparação entre estudantes.
 */

export type ReviewState = {
  repetitions: number;
  intervalDays: number;
  ease: number;
  dueAt: number;
};

export const DAY_MS = 86_400_000;

export const INITIAL_REVIEW: ReviewState = {
  repetitions: 0,
  intervalDays: 0,
  ease: 2.5,
  dueAt: 0,
};

/**
 * Implementação de referência (SM-2 adaptado), com validação de entrada.
 * `quality` vai de 0 (não lembrei) a 5 (acertei com facilidade).
 */
export function scheduleReview(
  current: ReviewState,
  quality: number,
  now = Date.now()
): ReviewState {
  if (!Number.isInteger(quality) || quality < 0 || quality > 5) {
    throw new RangeError("Invalid review quality");
  }
  const ease = Math.max(
    1.3,
    current.ease + 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
  );
  const repetitions = quality < 3 ? 0 : current.repetitions + 1;
  const base = Number.isFinite(current.intervalDays)
    ? Math.max(1, current.intervalDays)
    : 1;
  const intervalDays =
    repetitions <= 1
      ? 1
      : repetitions === 2
        ? 6
        : Math.max(1, Math.round(base * ease));
  return {
    repetitions,
    intervalDays,
    ease: Math.round(ease * 100) / 100,
    dueAt: now + intervalDays * DAY_MS,
  };
}

/** Aceita estado vindo do localStorage sem confiar nele. */
export function sanitizeReviewState(raw: unknown): ReviewState | null {
  if (!raw || typeof raw !== "object") return null;
  const value = raw as Record<string, unknown>;
  const repetitions = Number(value.repetitions);
  const intervalDays = Number(value.intervalDays);
  const ease = Number(value.ease);
  const dueAt = Number(value.dueAt);
  if (
    !Number.isInteger(repetitions) ||
    repetitions < 0 ||
    repetitions > 100 ||
    !Number.isFinite(intervalDays) ||
    intervalDays < 0 ||
    !Number.isFinite(ease) ||
    ease < 1.3 ||
    ease > 5 ||
    !Number.isFinite(dueAt) ||
    dueAt < 0
  ) {
    return null;
  }
  return { repetitions, intervalDays, ease, dueAt };
}

export type ReviewMap = Record<string, ReviewState>;

export function isDue(state: ReviewState, now = Date.now()): boolean {
  return state.repetitions === 0 || state.dueAt <= now;
}

export function dueModules(reviews: ReviewMap, now = Date.now()): string[] {
  return Object.entries(reviews)
    .filter(([, state]) => isDue(state, now))
    .sort((a, b) => a[1].dueAt - b[1].dueAt)
    .map(([moduleId]) => moduleId);
}

/** Qualidade a partir de acertos: sem nota, só evidência. */
export function qualityFromScore(correct: number, total: number): number {
  if (total <= 0) return 0;
  const ratio = correct / total;
  if (ratio >= 0.95) return 5;
  if (ratio >= 0.8) return 4;
  if (ratio >= 0.6) return 3;
  if (ratio >= 0.4) return 2;
  if (ratio > 0) return 1;
  return 0;
}

export type Mastery = "novo" | "em-andamento" | "consolidando" | "dominado";

export function masteryOf(
  attempts: { correct: boolean }[],
  reviews: ReviewMap,
  moduleId: string
): Mastery {
  if (!attempts.length) return "novo";
  const correct = attempts.filter(a => a.correct).length;
  const ratio = correct / attempts.length;
  const reviewed = reviews[moduleId];
  if (ratio >= 0.85 && reviewed && reviewed.repetitions >= 2) return "dominado";
  if (ratio >= 0.6) return "consolidando";
  return "em-andamento";
}

export const MASTERY_LABEL: Record<Mastery, string> = {
  novo: "Ainda sem atividade",
  "em-andamento": "Em andamento",
  consolidando: "Consolidando",
  dominado: "Dominado",
};
