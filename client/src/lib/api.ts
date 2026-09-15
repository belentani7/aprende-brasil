const API_BASE = import.meta.env.VITE_API_URL || "";

async function fetchJSON<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}

export type TrackData = {
  id: string;
  label: string;
  eyebrow: string;
  description: string;
  color: string;
  icon: string;
  target_modules: number;
  module_count: number;
};

export type ModuleData = {
  id: string;
  track_id: string;
  title: string;
  subtitle: string;
  level: string;
  level_order: number;
  duration_min: number;
  featured: boolean;
  accent: string;
  icon: string;
  steps?: StepData[];
};

export type StepData = {
  order: number;
  type: string;
  title: string;
  content: { text: string };
};

export type ModulesResponse = {
  total: number;
  page: number;
  per_page: number;
  items: ModuleData[];
};

export type StatsData = {
  total_modules: number;
  started: number;
  completed: number;
  overall_percent: number;
};

export const api = {
  getTracks: () => fetchJSON<TrackData[]>("/api/tracks"),

  getModules: (params: { track?: string; search?: string; page?: number }) => {
    const sp = new URLSearchParams();
    if (params.track) sp.set("track", params.track);
    if (params.search) sp.set("search", params.search);
    if (params.page) sp.set("page", String(params.page));
    return fetchJSON<ModulesResponse>(`/api/modules?${sp}`);
  },

  getFeatured: () => fetchJSON<ModuleData[]>("/api/modules/featured"),

  getModule: (id: string) => fetchJSON<ModuleData & { steps: StepData[] }>(`/api/modules/${id}`),

  askTutor: (message: string, subject: string) =>
    fetchJSON<{ answer: string; source: string }>("/api/tutor/ask", {
      method: "POST",
      body: JSON.stringify({ message, subject }),
    }),

  getStats: () => fetchJSON<StatsData>("/api/stats"),

  saveProgress: (moduleId: string, percent: number) =>
    fetchJSON<{ ok: boolean; percent: number }>("/api/progress", {
      method: "POST",
      body: JSON.stringify({ module_id: moduleId, percent }),
    }),

  getFavorites: () => fetchJSON<string[]>("/api/favorites"),

  toggleFavorite: (moduleId: string) =>
    fetchJSON<{ favorited: boolean }>("/api/favorites", {
      method: "POST",
      body: JSON.stringify({ module_id: moduleId }),
    }),
};
