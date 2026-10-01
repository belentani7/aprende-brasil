import { describe, expect, it } from "vitest";
import { MODULES } from "./curriculum";
import { answerTutor } from "./tutor";

const MIN_AMPLE = 250;

function byId(id: string) {
  const m = MODULES.find((x) => x.id === id);
  if (!m) throw new Error(`módulo ausente no currículo: ${id}`);
  return m;
}

describe("tutor Nilo (motor local)", () => {
  it("responde saudação com orientação ampla", () => {
    const { answer, source } = answerTutor("oi", "alfabetizacao");
    expect(source).toBe("local");
    expect(answer.length).toBeGreaterThan(MIN_AMPLE);
    expect(answer).toContain("Oi!");
    expect(answer).toMatch(/explicar|exercício|revis/i);
  });

  it("explica usando o conteúdo real do módulo", () => {
    const modulo = byId("mat-porcentagem");
    const { answer } = answerTutor("o que é porcentagem?", "matematica");
    const conceito = modulo.steps.find((s) => s.type === "explanation")!;
    expect(answer).toContain(conceito.content.text);
    expect(answer.length).toBeGreaterThan(MIN_AMPLE);
  });

  it("monta exercício com a etapa de prática do módulo", () => {
    const modulo = byId("mat-soma");
    const pratica = modulo.steps.find((s) => s.type === "practice")!;
    const { answer } = answerTutor("crie um exercício de soma", "matematica");
    expect(answer).toContain("Exercício");
    expect(answer).toContain(pratica.content.text);
  });

  it("faz revisão listando as cinco etapas", () => {
    const modulo = byId("alfa-letra-a");
    const { answer } = answerTutor("quero revisar a letra A", "alfabetizacao");
    expect(answer).toContain("Revisão");
    for (const step of modulo.steps) {
      expect(answer).toContain(step.title);
    }
  });

  it("acolhe quem travou, sem entregar a solução de imediato", () => {
    const { answer } = answerTutor("não entendi nada, muito difícil", "matematica");
    expect(answer).toContain("Calma");
    expect(answer.length).toBeGreaterThan(MIN_AMPLE);
  });

  it("responde com passo a passo quando pedem 'como'", () => {
    const { answer } = answerTutor("como faço para calcular o troco?", "matematica");
    expect(answer).toContain("Passo a passo");
    expect(answer.length).toBeGreaterThan(MIN_AMPLE);
  });

  it("sugere módulos quando não encontra o tema", () => {
    const { answer } = answerTutor("quero aprender xadrez quântico", "matematica");
    expect(answer).toContain("Não achei um módulo exato");
    expect(answer).toContain("•");
    expect(answer.length).toBeGreaterThan(MIN_AMPLE);
  });

  it("nunca devolve resposta curta demais", () => {
    const perguntas = [
      ["explica a internet", "informatica"],
      ["o que é cumprimentos em inglês?", "idiomas"],
      ["como uso o mouse", "informatica"],
      ["resumo de frações", "matematica"],
    ];
    for (const [msg, track] of perguntas) {
      const { answer } = answerTutor(msg, track);
      expect(answer.length, `resposta curta para: ${msg}`).toBeGreaterThan(MIN_AMPLE);
    }
  });
});
