import curriculum from "@/data/curriculum.json";
import type { ModuleWithSteps, TrackData } from "./types";

export const TRACKS = curriculum.tracks as TrackData[];
export const MODULES = curriculum.modules as ModuleWithSteps[];

export function findModule(id: string): ModuleWithSteps | undefined {
  return MODULES.find((m) => m.id === id);
}

export function trackLabel(id: string): string {
  return TRACKS.find((t) => t.id === id)?.label ?? id;
}
