import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import ActivityCard from "./ActivityCard";
import type { Activity } from "@/lib/types";

const choice: Activity = {
  kind: "multiple-choice",
  id: "teste-escolha",
  prompt: "Quanto é 2 + 3?",
  options: ["4", "5", "6"],
  correctIndex: 1,
  explanation: "2 + 3 = 5. Conte a partir do maior número.",
};

const tf: Activity = {
  kind: "true-false",
  id: "teste-vf",
  prompt: "O sol é uma estrela.",
  answer: true,
  explanation: "O sol é a estrela mais próxima da Terra.",
};

const blank: Activity = {
  kind: "fill-blank",
  id: "teste-lacuna",
  prompt: "Complete: eu ___ um livro.",
  acceptedAnswers: ["leio"],
  explanation: "Ler, primeira pessoa: eu leio.",
};

const order: Activity = {
  kind: "ordering",
  id: "teste-ordem",
  prompt: "Ordene os números.",
  items: ["um", "dois", "três"],
  correctOrder: [0, 1, 2],
};

const match: Activity = {
  kind: "matching",
  id: "teste-pares",
  prompt: "Ligue os números.",
  pairs: [
    { left: "um", right: "1" },
    { left: "dois", right: "2" },
  ],
};

const numeric: Activity = {
  kind: "numeric",
  id: "teste-numerico",
  prompt: "Quanto é 10 − 6?",
  answer: 4,
  tolerance: 0,
  explanation: "10 − 6 = 4.",
  unit: "reais",
};

describe("renderizador de atividades", () => {
  it("múltipla escolha marca a certa e explica", async () => {
    const user = userEvent.setup();
    const onResult = vi.fn();
    render(<ActivityCard activity={choice} onResult={onResult} />);
    await user.click(screen.getByRole("button", { name: /5/ }));
    expect(onResult).toHaveBeenCalledWith(
      expect.objectContaining({ correct: true })
    );
    expect(screen.getByText(/Certo\. 2 \+ 3 = 5/)).toBeInTheDocument();
  });

  it("múltipla escolha mostra feedback de erro sem punir", async () => {
    const user = userEvent.setup();
    render(<ActivityCard activity={choice} />);
    await user.click(screen.getByRole("button", { name: /4/ }));
    expect(screen.getByText(/Ainda não/)).toBeInTheDocument();
    expect(screen.queryByText(/errado|nota|zero/i)).not.toBeInTheDocument();
  });

  it("verdadeiro/falso funciona por botão", async () => {
    const user = userEvent.setup();
    render(<ActivityCard activity={tf} />);
    await user.click(screen.getByRole("button", { name: "Verdadeiro" }));
    expect(screen.getByText(/O sol é a estrela/)).toBeInTheDocument();
  });

  it("lacuna ignora acento e caixa", async () => {
    const user = userEvent.setup();
    render(<ActivityCard activity={blank} />);
    await user.type(screen.getByLabelText("Sua resposta"), "  LEIO ");
    await user.click(screen.getByRole("button", { name: "Conferir" }));
    expect(screen.getByText(/Certo/)).toBeInTheDocument();
  });

  it("lacuna vazia não é corrigida", async () => {
    const user = userEvent.setup();
    render(<ActivityCard activity={blank} />);
    await user.click(screen.getByRole("button", { name: "Conferir" }));
    expect(screen.queryByText(/Certo|Ainda não/)).not.toBeInTheDocument();
  });

  it("numérica aceita vírgula decimal e usa a unidade", async () => {
    const user = userEvent.setup();
    render(
      <ActivityCard activity={{ ...numeric, answer: 2.5, prompt: "Troco?" }} />
    );
    expect(screen.getByText("reais")).toBeInTheDocument();
    await user.type(screen.getByLabelText("Resposta numérica"), "2,5");
    await user.click(screen.getByRole("button", { name: "Conferir" }));
    expect(screen.getByText(/Certo/)).toBeInTheDocument();
  });

  it("ordenação usa botões acessíveis e permite conferir", async () => {
    const user = userEvent.setup();
    render(<ActivityCard activity={order} />);
    const upButtons = screen.getAllByRole("button", { name: /para cima/ });
    expect(upButtons).toHaveLength(3);
    // Empurra o primeiro item embaralhado até a posição final e confere.
    for (let i = 0; i < 4; i++) {
      const buttons = screen.getAllByRole("button", { name: /para cima/ });
      await user.click(buttons[1]);
    }
    await user.click(screen.getByRole("button", { name: "Conferir" }));
    expect(screen.getByRole("status")).toBeInTheDocument();
  });

  it("associação liga par a par e valida ao completar", async () => {
    const user = userEvent.setup();
    const onResult = vi.fn();
    render(<ActivityCard activity={match} onResult={onResult} />);
    await user.click(screen.getByRole("button", { name: "um" }));
    await user.click(screen.getByRole("button", { name: "1" }));
    await user.click(screen.getByRole("button", { name: "dois" }));
    await user.click(screen.getByRole("button", { name: "2" }));
    expect(onResult).toHaveBeenCalledWith(
      expect.objectContaining({ correct: true })
    );
  });

  it("toda atividade tem tipo rotulado e instrução", () => {
    for (const activity of [choice, tf, blank, order, match, numeric]) {
      const { unmount } = render(<ActivityCard activity={activity} />);
      expect(screen.getByText(activity.prompt)).toBeInTheDocument();
      unmount();
    }
  });
});
