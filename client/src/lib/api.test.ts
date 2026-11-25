import { describe, expect, it } from "vitest";
import { api } from "./api";
import { isoDate } from "./week";

const todayKey = isoDate(new Date());

describe("catálogo via API local", () => {
  it("pagina vinte módulos por vez dentro da trilha", async () => {
    const first = await api.getModules({ track: "alfabetizacao" });
    expect(first.total).toBe(93);
    expect(first.per_page).toBe(20);
    expect(first.items).toHaveLength(20);

    const last = await api.getModules({ track: "alfabetizacao", page: 5 });
    expect(last.items).toHaveLength(13);
  });

  it("busca em todas as trilhas quando há termo", async () => {
    const result = await api.getModules({
      track: "alfabetizacao",
      search: "porcentagem",
    });
    expect(result.total).toBeGreaterThan(0);
    expect(
      result.items.every(m => /porcentagem/i.test(`${m.title} ${m.subtitle}`))
    ).toBe(true);
  });

  it("filtra por título sem diferenciar maiúsculas", async () => {
    const result = await api.getModules({
      track: "matematica",
      search: "SOMAR",
    });
    expect(result.total).toBeGreaterThan(0);
    expect(result.items[0].track_id).toBe("matematica");
  });

  it("devolve destaques e trilhas fixas", async () => {
    const featured = await api.getFeatured();
    expect(featured.length).toBeGreaterThan(0);
    expect(featured.every(m => m.featured)).toBe(true);
    expect(await api.getTracks()).toHaveLength(4);
  });

  it("resolve um módulo com as cinco etapas", async () => {
    const module = await api.getModule("mat-porcentagem");
    expect(module.steps).toHaveLength(5);
    expect(module.steps.map(s => s.type)).toEqual([
      "explanation",
      "example",
      "practice",
      "check",
      "next",
    ]);
  });
});

describe("progresso no navegador", () => {
  it("é monotônico e registra as etapas concluídas", async () => {
    const first = await api.saveProgress("alfa-letra-a", 40, [1, 2]);
    expect(first.percent).toBe(40);

    const backwards = await api.saveProgress("alfa-letra-a", 20, [1]);
    expect(backwards.percent).toBe(40);
    expect(backwards.completed).toEqual([1]);

    const saved = await api.getModuleProgress("alfa-letra-a");
    expect(saved).toEqual({ percent: 40, completed: [1] });
  });

  it("não passa de 100 nem aceita valores inválidos", async () => {
    await api.saveProgress("mat-soma", 250, []);
    expect((await api.getModuleProgress("mat-soma")).percent).toBe(100);
    await api.saveProgress("mat-soma", Number.NaN, []);
    expect((await api.getModuleProgress("mat-soma")).percent).toBe(100);
  });

  it("soma apenas etapas novas à atividade do dia", async () => {
    await api.saveProgress("alfa-letra-a", 20, [1]);
    expect((await api.getActivity())[todayKey]).toBe(1);

    await api.saveProgress("alfa-letra-a", 40, [1, 2]);
    expect((await api.getActivity())[todayKey]).toBe(2);

    await api.saveProgress("alfa-letra-a", 40, [1, 2]);
    expect((await api.getActivity())[todayKey]).toBe(2);
  });

  it("resume o progresso do estudante", async () => {
    await api.saveProgress("alfa-letra-a", 100, [1, 2, 3, 4, 5]);
    await api.saveProgress("mat-soma", 50, [1]);
    const stats = await api.getStats();
    expect(stats.total_modules).toBe(205);
    expect(stats.started).toBe(2);
    expect(stats.completed).toBe(1);
    expect(stats.overall_percent).toBeCloseTo(0.7, 1);
  });

  it("tolera JSON corrompido no armazenamento", async () => {
    window.localStorage.setItem("aprende-brasil:progress", "{quebrado");
    expect(await api.getProgressMap()).toEqual({});
    expect((await api.getModuleProgress("alfa-letra-a")).percent).toBe(0);
  });
});

describe("favoritos", () => {
  it("alterna e persiste a lista", async () => {
    expect(await api.getFavorites()).toEqual([]);
    expect(await api.toggleFavorite("alfa-letra-a")).toEqual({
      favorited: true,
    });
    expect(await api.getFavorites()).toEqual(["alfa-letra-a"]);
    expect(await api.toggleFavorite("alfa-letra-a")).toEqual({
      favorited: false,
    });
    expect(await api.getFavorites()).toEqual([]);
  });
});
