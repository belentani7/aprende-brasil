import { MODULES, TRACKS } from "./curriculum";
import { answerTutor } from "./tutor";
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
  ModulesResponse,
  StatsData,
  StepData,
  TrackData,
  TutorReply,
};

const API_BASE = import.meta.env.VITE_API_URL || "";

const PER_PAGE = 20;
const PROGRESS_KEY = "aprende-brasil:progress";
const FAVORITES_KEY = "aprende-brasil:favorites";

type ProgressMap = Record<string, number>;

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
  subject: string,
): Promise<TutorReply> {
  const res = await fetch(`${API_BASE}/api/tutor/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, subject }),
  });
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return (await res.json()) as TutorReply;
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
    const filtered = MODULES.filter((m) => {
      if (track && m.track_id !== track) return false;
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
    MODULES.filter((m) => m.featured).slice(0, 6),

  getModule: async (id: string): Promise<ModuleWithSteps> => {
    const found = MODULES.find((m) => m.id === id);
    if (!found) throw new Error("Módulo não encontrado");
    return found;
  },

  askTutor: async (message: string, subject: string): Promise<TutorReply> => {
    if (API_BASE) {
      try {
        return await askRemoteTutor(message, subject);
      } catch {
        /* sem backend: usa o motor local */
      }
    }
    return answerTutor(message, subject);
  },

  getStats: async (): Promise<StatsData> => {
    const progress = readStore<ProgressMap>(PROGRESS_KEY, {});
    const values = Object.values(progress);
    const total = MODULES.length;
    return {
      total_modules: total,
      started: values.length,
      completed: values.filter((p) => p >= 100).length,
      overall_percent: total
        ? Math.round((values.reduce((a, b) => a + b, 0) / total) * 10) / 10
        : 0,
    };
  },

  saveProgress: async (
    moduleId: string,
    percent: number,
  ): Promise<{ ok: boolean; percent: number }> => {
    const progress = readStore<ProgressMap>(PROGRESS_KEY, {});
    const next = Math.max(progress[moduleId] ?? 0, percent);
    progress[moduleId] = next;
    writeStore(PROGRESS_KEY, progress);
    return { ok: true, percent: next };
  },

  getFavorites: async (): Promise<string[]> =>
    readStore<string[]>(FAVORITES_KEY, []),

  toggleFavorite: async (moduleId: string): Promise<{ favorited: boolean }> => {
    const favorites = readStore<string[]>(FAVORITES_KEY, []);
    const has = favorites.includes(moduleId);
    const next = has
      ? favorites.filter((id) => id !== moduleId)
      : [...favorites, moduleId];
    writeStore(FAVORITES_KEY, next);
    return { favorited: !has };
  },
};
