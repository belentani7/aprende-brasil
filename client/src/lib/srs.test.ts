import { describe, expect, it } from "vitest";
import {
  DAY_MS,
  INITIAL_REVIEW,
  dueModules,
  isDue,
  masteryOf,
  qualityFromScore,
  sanitizeReviewState,
  scheduleReview,
  type ReviewState,
} from "./srs";

const NOW = Date.UTC(2026, 10, 25, 12, 0, 0);

describe("revisão espaçada", () => {
  it("primeira repetição volta em 1 dia", () => {
    const next = scheduleReview(INITIAL_REVIEW, 4, NOW);
    expect(next.repetitions).toBe(1);
    expect(next.intervalDays).toBe(1);
    expect(next.dueAt).toBe(NOW + DAY_MS);
  });

  it("segunda repetição volta em 6 dias", () => {
    const first = scheduleReview(INITIAL_REVIEW, 5, NOW);
    const second = scheduleReview(first, 5, NOW);
    expect(second.repetitions).toBe(2);
    expect(second.intervalDays).toBe(6);
  });

  it("terceira repetição multiplica pelo ease e cresce", () => {
    let state = INITIAL_REVIEW;
    for (let i = 0; i < 3; i++) state = scheduleReview(state, 5, NOW);
    expect(state.repetitions).toBe(3);
    expect(state.intervalDays).toBeGreaterThan(6);
  });

  it("erro zera repetições mas mantém o ease mínimo", () => {
    let state = INITIAL_REVIEW;
    for (let i = 0; i < 4; i++) state = scheduleReview(state, 5, NOW);
    const failed = scheduleReview(state, 1, NOW);
    expect(failed.repetitions).toBe(0);
    expect(failed.intervalDays).toBe(1);
    expect(failed.ease).toBeGreaterThanOrEqual(1.3);
  });

  it("ease nunca cai abaixo de 1.3 mesmo com muitos erros", () => {
    let state: ReviewState = { ...INITIAL_REVIEW };
    for (let i = 0; i < 20; i++) state = scheduleReview(state, 0, NOW);
    expect(state.ease).toBeGreaterThanOrEqual(1.3);
  });

  it("rejeita qualidade inválida", () => {
    expect(() => scheduleReview(INITIAL_REVIEW, 6)).toThrow(RangeError);
    expect(() => scheduleReview(INITIAL_REVIEW, -1)).toThrow(RangeError);
    expect(() => scheduleReview(INITIAL_REVIEW, 3.5)).toThrow(RangeError);
  });

  it("estado corrompido é descartado ao ler do armazenamento", () => {
    expect(sanitizeReviewState(null)).toBeNull();
    expect(
      sanitizeReviewState({
        repetitions: -1,
        intervalDays: 1,
        ease: 2,
        dueAt: 0,
      })
    ).toBeNull();
    expect(
      sanitizeReviewState({
        repetitions: 1,
        intervalDays: 1,
        ease: 9,
        dueAt: 0,
      })
    ).toBeNull();
    expect(
      sanitizeReviewState({
        repetitions: 1,
        intervalDays: 1,
        ease: 2.5,
        dueAt: 10,
      })
    ).toEqual({ repetitions: 1, intervalDays: 1, ease: 2.5, dueAt: 10 });
  });

  it("lista pendências ordenadas pelo vencimento", () => {
    const reviews = {
      a: { repetitions: 2, intervalDays: 6, ease: 2.5, dueAt: NOW - 1000 },
      b: { repetitions: 2, intervalDays: 6, ease: 2.5, dueAt: NOW + DAY_MS },
      c: { repetitions: 0, intervalDays: 0, ease: 2.5, dueAt: 0 },
    };
    expect(dueModules(reviews, NOW)).toEqual(["c", "a"]);
    expect(isDue(reviews.b, NOW)).toBe(false);
  });

  it("qualidade deriva dos acertos, sem nota", () => {
    expect(qualityFromScore(2, 2)).toBe(5);
    expect(qualityFromScore(4, 5)).toBe(4);
    expect(qualityFromScore(3, 5)).toBe(3);
    expect(qualityFromScore(2, 5)).toBe(2);
    expect(qualityFromScore(1, 3)).toBe(1);
    expect(qualityFromScore(0, 4)).toBe(0);
    expect(qualityFromScore(0, 0)).toBe(0);
  });

  it("domínio exige acerto alto e revisão acumulada", () => {
    const attempts = [{ correct: true }, { correct: true }, { correct: true }];
    expect(masteryOf([], {}, "x")).toBe("novo");
    expect(masteryOf(attempts, {}, "x")).toBe("consolidando");
    expect(
      masteryOf(
        attempts,
        { x: { repetitions: 2, intervalDays: 6, ease: 2.5, dueAt: 0 } },
        "x"
      )
    ).toBe("dominado");
    expect(masteryOf([{ correct: false }, { correct: false }], {}, "y")).toBe(
      "em-andamento"
    );
  });
});
