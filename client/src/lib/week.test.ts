import { describe, expect, it } from "vitest";
import { buildWeek, isoDate, streak } from "./week";

describe("semana de atividade", () => {
  const today = new Date(2026, 10, 25); // 25/11/2026, quarta-feira

  it("devolve exatamente os últimos sete dias, terminando hoje", () => {
    const week = buildWeek(today, {});
    expect(week).toHaveLength(7);
    expect(week[0].key).toBe("2026-11-19");
    expect(week[6].key).toBe("2026-11-25");
    expect(week[6].isToday).toBe(true);
    expect(week.filter(day => day.isToday)).toHaveLength(1);
  });

  it("rotula os dias em português e preenche o dia do mês", () => {
    const week = buildWeek(today, {});
    expect(week.map(day => day.label)).toEqual([
      "QUI",
      "SEX",
      "SÁB",
      "DOM",
      "SEG",
      "TER",
      "QUA",
    ]);
    expect(week[0].day).toBe("19");
    expect(week[6].day).toBe("25");
  });

  it("usa a contagem registrada e ignora valores inválidos", () => {
    const week = buildWeek(today, {
      "2026-11-25": 4,
      "2026-11-24": Number.NaN,
      "2026-11-23": -3,
    });
    expect(week[6].steps).toBe(4);
    expect(week[5].steps).toBe(0);
    expect(week[4].steps).toBe(0);
  });

  it("atravessa a virada de mês e de ano sem buracos", () => {
    const week = buildWeek(new Date(2027, 0, 2), { "2026-12-31": 2 });
    expect(week[0].key).toBe("2026-12-27");
    expect(week[6].key).toBe("2027-01-02");
    expect(week.find(day => day.key === "2026-12-31")?.steps).toBe(2);
  });

  it("formata a data local no padrão ISO sem depender de fuso", () => {
    expect(isoDate(new Date(2026, 0, 5))).toBe("2026-01-05");
  });
});

describe("sequência de dias", () => {
  const today = new Date(2026, 10, 25);

  it("conta dias consecutivos até hoje", () => {
    expect(
      streak(
        { "2026-11-25": 1, "2026-11-24": 2, "2026-11-23": 1, "2026-11-21": 5 },
        today
      )
    ).toBe(3);
  });

  it("zera quando hoje ainda não teve atividade", () => {
    expect(streak({ "2026-11-24": 2 }, today)).toBe(0);
  });
});
