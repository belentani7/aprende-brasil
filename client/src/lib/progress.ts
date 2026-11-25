import { sanitizeReviewState, type ReviewMap } from "./srs";

/**
 * Camada única de armazenamento local.
 *
 * Chaves versionadas, leitura tolerante (dado corrompido não derruba a tela) e
 * exportação/importação completas. O formato do arquivo exportado é o mesmo do
 * endpoint `/api/export`, então dá para levar o progresso do navegador para uma
 * sessão sincronizada sem conversão.
 */

export const STORAGE_VERSION = 1;

export const KEYS = {
  progress: "aprende-brasil:progress",
  steps: "aprende-brasil:completed-steps",
  favorites: "aprende-brasil:favorites",
  activity: "aprende-brasil:activity",
  attempts: "aprende-brasil:attempts",
  reviews: "aprende-brasil:reviews",
  exportedAt: "aprende-brasil:last-export",
} as const;

export type Attempt = {
  moduleId: string;
  activityId: string;
  correct: boolean;
  at: number;
};

export type ProgressSnapshot = {
  version: number;
  exported_at: string;
  progress: Record<string, number>;
  completed: Record<string, number[]>;
  favorites: string[];
  activity?: Record<string, number>;
  attempts?: Attempt[];
  reviews?: ReviewMap;
};

export function readStore<T>(key: string, fallback: T): T {
  if (typeof window === "undefined" || !window.localStorage) return fallback;
  try {
    const raw = window.localStorage.getItem(key);
    return raw ? (JSON.parse(raw) as T) : fallback;
  } catch {
    return fallback;
  }
}

export function writeStore(key: string, value: unknown): boolean {
  if (typeof window === "undefined" || !window.localStorage) return false;
  try {
    window.localStorage.setItem(key, JSON.stringify(value));
    return true;
  } catch {
    return false;
  }
}

export function clampPercent(value: number): number {
  if (!Number.isFinite(value)) return 0;
  return Math.min(100, Math.max(0, value));
}

/** Mantém só valores plausíveis por módulo. */
export function sanitizeProgress(raw: unknown): Record<string, number> {
  if (!raw || typeof raw !== "object") return {};
  const result: Record<string, number> = {};
  for (const [key, value] of Object.entries(raw as Record<string, unknown>)) {
    const num = Number(value);
    if (typeof key === "string" && key && Number.isFinite(num)) {
      result[key] = clampPercent(num);
    }
  }
  return result;
}

export function sanitizeCompleted(raw: unknown): Record<string, number[]> {
  if (!raw || typeof raw !== "object") return {};
  const result: Record<string, number[]> = {};
  for (const [key, value] of Object.entries(raw as Record<string, unknown>)) {
    if (!Array.isArray(value)) continue;
    const orders = Array.from(
      new Set(
        value.map(Number).filter(n => Number.isInteger(n) && n >= 1 && n <= 50)
      )
    ).sort((a, b) => a - b);
    result[key] = orders;
  }
  return result;
}

export function sanitizeFavorites(raw: unknown): string[] {
  if (!Array.isArray(raw)) return [];
  return Array.from(
    new Set(
      raw.filter((item): item is string => typeof item === "string" && !!item)
    )
  );
}

export function sanitizeAttempts(raw: unknown): Attempt[] {
  if (!Array.isArray(raw)) return [];
  return raw
    .filter(
      (item): item is Attempt =>
        !!item &&
        typeof item === "object" &&
        typeof (item as Attempt).moduleId === "string" &&
        typeof (item as Attempt).activityId === "string" &&
        typeof (item as Attempt).correct === "boolean"
    )
    .map(item => ({
      ...item,
      at: Number.isFinite(item.at) ? item.at : 0,
    }))
    .slice(-2000);
}

export function sanitizeReviews(raw: unknown): ReviewMap {
  if (!raw || typeof raw !== "object") return {};
  const result: ReviewMap = {};
  for (const [key, value] of Object.entries(raw as Record<string, unknown>)) {
    const state = sanitizeReviewState(value);
    if (state) result[key] = state;
  }
  return result;
}

/** Lê o estado inteiro, descartando o que estiver corrompido. */
export function readSnapshot(now = new Date()): ProgressSnapshot {
  return {
    version: STORAGE_VERSION,
    exported_at: now.toISOString(),
    progress: sanitizeProgress(readStore(KEYS.progress, {})),
    completed: sanitizeCompleted(readStore(KEYS.steps, {})),
    favorites: sanitizeFavorites(readStore(KEYS.favorites, [])),
    activity: readStore<Record<string, number>>(KEYS.activity, {}),
    attempts: sanitizeAttempts(readStore(KEYS.attempts, [])),
    reviews: sanitizeReviews(readStore(KEYS.reviews, {})),
  };
}

export function exportProgress(): ProgressSnapshot {
  const snapshot = readSnapshot();
  writeStore(KEYS.exportedAt, snapshot.exported_at);
  return snapshot;
}

export type ImportResult = {
  ok: boolean;
  modules: number;
  favorites: number;
  ignored: string[];
};

/**
 * Importa um arquivo exportado. `replace=false` (padrão) nunca reduz progresso.
 * Dados inválidos são ignorados um a um, não derrubam a importação inteira.
 */
export function importProgress(
  payload: unknown,
  options: { replace?: boolean; validIds?: Set<string> } = {}
): ImportResult {
  const { replace = false, validIds } = options;
  if (!payload || typeof payload !== "object") {
    return {
      ok: false,
      modules: 0,
      favorites: 0,
      ignored: ["arquivo inválido"],
    };
  }
  const data = payload as Record<string, unknown>;
  const version = Number(data.version);
  if (version !== STORAGE_VERSION) {
    return {
      ok: false,
      modules: 0,
      favorites: 0,
      ignored: ["versão incompatível"],
    };
  }

  const incomingProgress = sanitizeProgress(data.progress);
  const incomingCompleted = sanitizeCompleted(data.completed);
  const incomingFavorites = sanitizeFavorites(data.favorites);
  const ignored: string[] = [];

  const progress = replace ? {} : readSnapshot().progress;
  const completed = replace ? {} : sanitizeCompleted(readStore(KEYS.steps, {}));
  const favorites = replace
    ? []
    : sanitizeFavorites(readStore(KEYS.favorites, []));

  let modules = 0;
  for (const [moduleId, percent] of Object.entries(incomingProgress)) {
    if (validIds && !validIds.has(moduleId)) {
      ignored.push(moduleId);
      continue;
    }
    progress[moduleId] = replace
      ? percent
      : Math.max(progress[moduleId] ?? 0, percent);
    const merged = new Set([
      ...(completed[moduleId] ?? []),
      ...(incomingCompleted[moduleId] ?? []),
    ]);
    if (merged.size) completed[moduleId] = [...merged].sort((a, b) => a - b);
    modules += 1;
  }
  for (const moduleId of Object.keys(incomingCompleted)) {
    if (progress[moduleId] === undefined) {
      if (validIds && !validIds.has(moduleId)) {
        ignored.push(moduleId);
        continue;
      }
      const merged = new Set(incomingCompleted[moduleId]);
      completed[moduleId] = [...merged].sort((a, b) => a - b);
      progress[moduleId] = Math.max(progress[moduleId] ?? 0, 0);
      modules += 1;
    }
  }

  let favoriteCount = 0;
  for (const moduleId of incomingFavorites) {
    if (validIds && !validIds.has(moduleId)) {
      ignored.push(moduleId);
      continue;
    }
    if (!favorites.includes(moduleId)) {
      favorites.push(moduleId);
      favoriteCount += 1;
    }
  }

  writeStore(KEYS.progress, progress);
  writeStore(KEYS.steps, completed);
  writeStore(KEYS.favorites, favorites);

  const incomingReviews = sanitizeReviews(data.reviews);
  if (Object.keys(incomingReviews).length) {
    const reviews = replace ? {} : sanitizeReviews(readStore(KEYS.reviews, {}));
    writeStore(KEYS.reviews, { ...reviews, ...incomingReviews });
  }

  return { ok: true, modules, favorites: favoriteCount, ignored };
}

export function resetProgress(): void {
  writeStore(KEYS.progress, {});
  writeStore(KEYS.steps, {});
  writeStore(KEYS.favorites, []);
  writeStore(KEYS.activity, {});
  writeStore(KEYS.attempts, []);
  writeStore(KEYS.reviews, {});
}
