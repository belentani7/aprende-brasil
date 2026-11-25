import { getModuleWithSteps, MODULES, TRACKS } from "./curriculum";
import {
  clampPercent,
  exportProgress,
  importProgress,
  KEYS,
  readSnapshot,
  readStore,
  resetProgress,
  sanitizeAttempts,
  sanitizeReviews,
  writeStore,
  type Attempt,
  type ImportResult,
  type ProgressSnapshot,
} from "./progress";
import { qualityFromScore, scheduleReview, type ReviewMap } from "./srs";
import { isoDate } from "./week";
import type {
  ActivityAttempt,
  ModuleData,
  ModuleWithSteps,
  ModulesResponse,
  StatsData,
  StepData,
  TrackData,
  TutorReply,
} from "./types";

export type {
  ModuleData,
  ModuleWithSteps,
  ModulesResponse,
  StatsData,
  StepData,
  TrackData,
  TutorReply,
};

const API_BASE = import.meta.env.VITE_API_URL || "";

const PER_PAGE = 20;

type ProgressMap = Record<string, number>;
type CompletedMap = Record<string, number[]>;

export type ModuleProgress = {
  percent: number;
  completed: number[];
};

const MODULE_IDS = new Set(MODULES.map(m => m.id));

async function askRemoteTutor(
  message: string,
  subject: string
): Promise<TutorReply> {
  const res = await fetch(`${API_BASE}/api/tutor/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, subject }),
  });
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return (await res.json()) as TutorReply;
}

/**
 * O motor local do tutor é grande (índice dos 205 módulos) e só é útil quando
 * a pessoa abre o painel. Por isso é importado sob demanda: a primeira visita
 * não paga esse custo.
 */
async function askLocalTutor(
  message: string,
  subject: string
): Promise<TutorReply> {
  const { answerTutor } = await import("./tutor");
  return answerTutor(message, subject);
}

export const api = {
  getTracks: async (): Promise<TrackData[]> => TRACKS,

  getModules: async (params: {
    track?: string;
    search?: string;
    page?: number;
  }): Promise<ModulesResponse> => {
    const { track, search, page = 1 } = params;
    const term = search?.trim().toLowerCase();
    const filtered = MODULES.filter(m => {
      // Com termo de busca, procura em todas as trilhas: quem digita
      // "porcentagem" quer achar o módulo, não receber "nada encontrado"
      // só porque a trilha aberta é outra.
      if (track && !term && m.track_id !== track) return false;
      if (term) {
        const haystack = `${m.title} ${m.subtitle ?? ""}`.toLowerCase();
        if (!haystack.includes(term)) return false;
      }
      return true;
    });
    const start = (page - 1) * PER_PAGE;
    return {
      total: filtered.length,
      page,
      per_page: PER_PAGE,
      items: filtered.slice(start, start + PER_PAGE),
    };
  },

  getFeatured: async (): Promise<ModuleData[]> =>
    MODULES.filter(m => m.featured).slice(0, 6),

  getModule: async (id: string): Promise<ModuleWithSteps> =>
    getModuleWithSteps(id),

  askTutor: async (message: string, subject: string): Promise<TutorReply> => {
    if (API_BASE) {
      try {
        return await askRemoteTutor(message, subject);
      } catch {
        /* sem backend: usa o motor local */
      }
    }
    return askLocalTutor(message, subject);
  },

  getStats: async (): Promise<StatsData> => {
    const progress = readStore<ProgressMap>(KEYS.progress, {});
    const values = Object.values(progress);
    const total = MODULES.length;
    return {
      total_modules: total,
      started: values.length,
      completed: values.filter(p => p >= 100).length,
      overall_percent: total
        ? Math.round((values.reduce((a, b) => a + b, 0) / total) * 10) / 10
        : 0,
    };
  },

  /** Percentual já alcançado por módulo (usado no catálogo da tela inicial). */
  getProgressMap: async (): Promise<Record<string, number>> =>
    readStore<ProgressMap>(KEYS.progress, {}),

  getModuleProgress: async (moduleId: string): Promise<ModuleProgress> => {
    const percent = clampPercent(
      readStore<ProgressMap>(KEYS.progress, {})[moduleId] ?? 0
    );
    const completed = readStore<CompletedMap>(KEYS.steps, {})[moduleId] ?? [];
    return { percent, completed: [...completed].sort((a, b) => a - b) };
  },

  /**
   * Progresso é monotônico (como na API FastAPI): desmarcar uma etapa não
   * apaga o que a pessoa já conquistou. O percentual fica em [0, 100].
   */
  saveProgress: async (
    moduleId: string,
    percent: number,
    completed?: number[]
  ): Promise<ModuleProgress> => {
    const progress = readStore<ProgressMap>(KEYS.progress, {});
    const next = Math.max(progress[moduleId] ?? 0, clampPercent(percent));
    progress[moduleId] = next;
    writeStore(KEYS.progress, progress);

    if (completed) {
      const steps = readStore<CompletedMap>(KEYS.steps, {});
      const previous = steps[moduleId] ?? [];
      steps[moduleId] = Array.from(new Set(completed)).sort((a, b) => a - b);
      writeStore(KEYS.steps, steps);

      const fresh = steps[moduleId].filter(
        order => !previous.includes(order)
      ).length;
      if (fresh > 0) {
        const activity = readStore<Record<string, number>>(KEYS.activity, {});
        const key = isoDate(new Date());
        activity[key] = (activity[key] ?? 0) + fresh;
        writeStore(KEYS.activity, activity);
      }
    }

    return {
      percent: next,
      completed: readStore<CompletedMap>(KEYS.steps, {})[moduleId] ?? [],
    };
  },

  /** Atividade diária real (etapas marcadas por dia), para o painel semanal. */
  getActivity: async (): Promise<Record<string, number>> =>
    readStore<Record<string, number>>(KEYS.activity, {}),

  /** Registra uma tentativa de atividade (evidência real de aprendizagem). */
  recordAttempt: async (
    attempt: Omit<ActivityAttempt, "at">
  ): Promise<void> => {
    const attempts = sanitizeAttempts(readStore<Attempt[]>(KEYS.attempts, []));
    attempts.push({ ...attempt, at: Date.now() });
    writeStore(KEYS.attempts, attempts.slice(-2000));
  },

  getAttempts: async (): Promise<ActivityAttempt[]> =>
    sanitizeAttempts(readStore<Attempt[]>(KEYS.attempts, [])),

  /**
   * Fecha um módulo: agenda a revisão espaçada a partir do desempenho nas
   * atividades. Sem atividades respondidas, a qualidade é neutra (3) e o
   * módulo volta em 1 dia — completar página não é domínio.
   */
  completeModule: async (moduleId: string): Promise<string> => {
    const attempts = sanitizeAttempts(
      readStore<Attempt[]>(KEYS.attempts, [])
    ).filter(a => a.moduleId === moduleId);
    const correct = attempts.filter(a => a.correct).length;
    const quality = attempts.length
      ? qualityFromScore(correct, attempts.length)
      : 3;
    const reviews = sanitizeReviews(readStore<ReviewMap>(KEYS.reviews, {}));
    reviews[moduleId] = scheduleReview(
      reviews[moduleId] ?? {
        repetitions: 0,
        intervalDays: 0,
        ease: 2.5,
        dueAt: 0,
      },
      quality
    );
    writeStore(KEYS.reviews, reviews);
    return reviews[moduleId].intervalDays === 1
      ? "Revisão marcada para amanhã."
      : `Revisão marcada para daqui a ${reviews[moduleId].intervalDays} dias.`;
  },

  getReviews: async (): Promise<ReviewMap> =>
    sanitizeReviews(readStore<ReviewMap>(KEYS.reviews, {})),

  /** Exportação completa (progresso, etapas, favoritos, tentativas, revisões). */
  exportData: async (): Promise<ProgressSnapshot> => exportProgress(),

  importData: async (payload: unknown): Promise<ImportResult> =>
    importProgress(payload, { validIds: MODULE_IDS }),

  resetData: async (): Promise<void> => resetProgress(),

  /** Resumo usado pela tela de progresso. */
  getSummary: async () => {
    const snapshot = readSnapshot();
    const values = Object.values(snapshot.progress);
    const attempts = snapshot.attempts ?? [];
    const correct = attempts.filter(a => a.correct).length;
    return {
      total_modules: MODULES.length,
      started: values.length,
      completed: values.filter(p => p >= 100).length,
      overall_percent: MODULES.length
        ? Math.round(
            (values.reduce((a, b) => a + b, 0) / MODULES.length) * 10
          ) / 10
        : 0,
      activities_answered: attempts.length,
      activities_correct: correct,
      activities_accuracy: attempts.length
        ? Math.round((correct / attempts.length) * 100)
        : null,
      favorites: snapshot.favorites.length,
      reviews_due: Object.values(snapshot.reviews ?? {}).filter(
        state => state.repetitions === 0 || state.dueAt <= Date.now()
      ).length,
    };
  },

  getFavorites: async (): Promise<string[]> =>
    readStore<string[]>(KEYS.favorites, []),

  toggleFavorite: async (moduleId: string): Promise<{ favorited: boolean }> => {
    const favorites = readStore<string[]>(KEYS.favorites, []);
    const has = favorites.includes(moduleId);
    const next = has
      ? favorites.filter(id => id !== moduleId)
      : [...favorites, moduleId];
    writeStore(KEYS.favorites, next);
    return { favorited: !has };
  },
};
