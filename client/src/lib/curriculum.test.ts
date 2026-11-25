import { describe, expect, it } from "vitest";
import stepsByModule from "@/data/curriculum-steps.json";
import {
  clampPercent,
  findModule,
  getModuleWithSteps,
  loadStepMap,
  MODULES,
  TRACKS,
  trackCoverage,
  trackLabel,
} from "./curriculum";
import type { StepData } from "./types";

const STEP_TYPES = ["explanation", "example", "practice", "check", "next"];

describe("catálogo estático", () => {
  it("tem quatro trilhas e 205 módulos, como o README promete", () => {
    expect(TRACKS).toHaveLength(4);
    expect(MODULES).toHaveLength(205);
  });

  it("não repete ids e mantém cada módulo na sua trilha", () => {
    expect(new Set(MODULES.map(m => m.id)).size).toBe(MODULES.length);
    const trackIds = new Set(TRACKS.map(t => t.id));
    for (const module of MODULES) {
      expect(trackIds.has(module.track_id), module.id).toBe(true);
    }
  });

  it("declara step_count coerente com as etapas exportadas", () => {
    for (const module of MODULES) {
      expect(module.step_count, module.id).toBe(5);
      expect(
        stepsByModule[module.id as keyof typeof stepsByModule],
        module.id
      ).toHaveLength(5);
    }
  });
});

describe("etapas sob demanda", () => {
  it("exporta 1.025 etapas nas cinco etapas canônicas, em ordem", async () => {
    const steps = await loadStepMap();
    const all = Object.values(steps).flat() as StepData[];
    expect(all).toHaveLength(1025);
    for (const [id, list] of Object.entries(steps)) {
      expect(
        list.map(step => step.order),
        id
      ).toEqual([1, 2, 3, 4, 5]);
      expect(
        list.map(step => step.type),
        id
      ).toEqual(STEP_TYPES);
      for (const step of list) {
        expect(
          step.content?.text?.trim().length ?? 0,
          `${id}/${step.order}`
        ).toBeGreaterThanOrEqual(20);
      }
    }
  });

  it("carrega um módulo completo pelo id", async () => {
    const module = await getModuleWithSteps("alfa-letra-a");
    expect(module.title).toBe("A letra A");
    expect(module.steps).toHaveLength(5);
    expect(module.steps[0].type).toBe("explanation");
  });

  it("rejeita módulo inexistente com erro claro", async () => {
    await expect(getModuleWithSteps("nao-existe")).rejects.toThrow(
      "Módulo não encontrado"
    );
  });
});

describe("utilidades do catálogo", () => {
  it("encontra módulos e rótulos de trilha", () => {
    expect(findModule("mat-soma")?.title).toBe("Somar com as mãos");
    expect(trackLabel("idiomas")).toBe("Idiomas");
    expect(trackLabel("desconhecida")).toBe("desconhecida");
  });

  it("calcula cobertura sem divisão por zero", () => {
    const withTarget = { ...TRACKS[0], module_count: 30, target_modules: 60 };
    expect(trackCoverage(withTarget)).toBe(50);
    const noTarget = { ...TRACKS[0], module_count: 93, target_modules: 0 };
    expect(trackCoverage(noTarget)).toBe(100);
    const impossible = { ...TRACKS[0], module_count: 120, target_modules: 60 };
    expect(trackCoverage(impossible)).toBe(100);
  });

  it("limita percentuais a [0, 100] e trata valores inválidos", () => {
    expect(clampPercent(-10)).toBe(0);
    expect(clampPercent(140)).toBe(100);
    expect(clampPercent(Number.NaN)).toBe(0);
    expect(clampPercent(42.5)).toBe(42.5);
  });
});
