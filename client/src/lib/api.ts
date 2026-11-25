import { getModuleWithSteps, MODULES, TRACKS } from "./curriculum";
import { isoDate } from "./week";
import type {
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
const PROGRESS_KEY = "aprende-brasil:progress";
const STEPS_KEY = "aprende-brasil:completed-steps";
const FAVORITES_KEY = "aprende-brasil:favorites";
const ACTIVITY_KEY = "aprende-brasil:activity";

type ProgressMap = Record<string, number>;
type CompletedMap = Record<string, number[]>;

export type ModuleProgress = {
  percent: number;
  completed: number[];
};

function clampPercent(value: number): number {
  if (!Number.isFinite(value)) return 0;
  return Math.min(100, Math.max(0, value));
}

function readStore<T>(key: string, fallback: T): T {
  try {
    const raw = window.localStorage.getItem(key);
    return raw ? (JSON.parse(raw) as T) : fallback;
  } catch {
    return fallback;
  }
}

function writeStore(key: string, value: unknown): void {
  try {
    window.localStorage.setItem(key, JSON.stringify(value));
  } catch {
    /* modo privado / quota: mantém em memória */
  }
}

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
    const progress = readStore<ProgressMap>(PROGRESS_KEY, {});
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
    readStore<ProgressMap>(PROGRESS_KEY, {}),

  getModuleProgress: async (moduleId: string): Promise<ModuleProgress> => {
    const percent = clampPercent(
      readStore<ProgressMap>(PROGRESS_KEY, {})[moduleId] ?? 0
    );
    const completed = readStore<CompletedMap>(STEPS_KEY, {})[moduleId] ?? [];
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
    const progress = readStore<ProgressMap>(PROGRESS_KEY, {});
    const next = Math.max(progress[moduleId] ?? 0, clampPercent(percent));
    progress[moduleId] = next;
    writeStore(PROGRESS_KEY, progress);

    if (completed) {
      const steps = readStore<CompletedMap>(STEPS_KEY, {});
      const previous = steps[moduleId] ?? [];
      steps[moduleId] = Array.from(new Set(completed)).sort((a, b) => a - b);
      writeStore(STEPS_KEY, steps);

      const fresh = steps[moduleId].filter(
        order => !previous.includes(order)
      ).length;
      if (fresh > 0) {
        const activity = readStore<Record<string, number>>(ACTIVITY_KEY, {});
        const key = isoDate(new Date());
        activity[key] = (activity[key] ?? 0) + fresh;
        writeStore(ACTIVITY_KEY, activity);
      }
    }

    return {
      percent: next,
      completed: readStore<CompletedMap>(STEPS_KEY, {})[moduleId] ?? [],
    };
  },

  /** Atividade diária real (etapas marcadas por dia), para o painel semanal. */
  getActivity: async (): Promise<Record<string, number>> =>
    readStore<Record<string, number>>(ACTIVITY_KEY, {}),

  getFavorites: async (): Promise<string[]> =>
    readStore<string[]>(FAVORITES_KEY, []),

  toggleFavorite: async (moduleId: string): Promise<{ favorited: boolean }> => {
    const favorites = readStore<string[]>(FAVORITES_KEY, []);
    const has = favorites.includes(moduleId);
    const next = has
      ? favorites.filter(id => id !== moduleId)
      : [...favorites, moduleId];
    writeStore(FAVORITES_KEY, next);
    return { favorited: !has };
  },
};
