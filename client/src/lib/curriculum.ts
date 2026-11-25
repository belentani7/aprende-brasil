import catalog from "@/data/curriculum.json";
import type { ModuleData, ModuleWithSteps, StepData, TrackData } from "./types";

/**
 * Catálogo leve: 4 trilhas + metadados dos 205 módulos (sem as etapas).
 * Vem no bundle inicial porque a tela inicial precisa listar e filtrar módulos.
 */
export const TRACKS = catalog.tracks as TrackData[];
export const MODULES = catalog.modules as ModuleData[];

/**
 * Etapas completas (1.025 textos). Ficam em um chunk próprio e só são
 * baixadas ao abrir um módulo — 34 KB gzip que a primeira visita não paga.
 */
let stepsPromise: Promise<Record<string, StepData[]>> | null = null;

export function loadStepMap(): Promise<Record<string, StepData[]>> {
  stepsPromise ??= import("@/data/curriculum-steps.json").then(
    mod => mod.default as Record<string, StepData[]>
  );
  return stepsPromise;
}

export function findModule(id: string): ModuleData | undefined {
  return MODULES.find(m => m.id === id);
}

export async function getModuleWithSteps(id: string): Promise<ModuleWithSteps> {
  const found = findModule(id);
  if (!found) throw new Error("Módulo não encontrado");
  const steps = await loadStepMap();
  return { ...found, steps: steps[id] ?? [] };
}

export function trackLabel(id: string): string {
  return TRACKS.find(t => t.id === id)?.label ?? id;
}

/** Cobertura do catálogo de uma trilha, sempre entre 0 e 100. */
export function trackCoverage(track: TrackData): number {
  const target =
    track.target_modules > 0 ? track.target_modules : track.module_count;
  return clampPercent(target ? (track.module_count / target) * 100 : 0);
}

export function clampPercent(value: number): number {
  if (!Number.isFinite(value)) return 0;
  return Math.min(100, Math.max(0, value));
}
