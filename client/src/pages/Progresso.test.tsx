import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { Router } from "wouter";
import { memoryLocation } from "wouter/memory-location";
import Progresso from "./Progresso";

vi.mock("sonner", () => ({
  toast: Object.assign(vi.fn(), {
    success: vi.fn(),
    error: vi.fn(),
    info: vi.fn(),
  }),
}));

function renderPage() {
  const { hook } = memoryLocation({ path: "/progresso", static: true });
  return render(
    <Router hook={hook}>
      <Progresso />
    </Router>
  );
}

describe("página de progresso", () => {
  beforeEach(() => {
    window.localStorage.clear();
    vi.stubGlobal("confirm", () => true);
    vi.stubGlobal("URL", {
      ...URL,
      createObjectURL: () => "blob:fake",
      revokeObjectURL: () => {},
    });
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("mostra zebras honestas quando não há atividade respondida", async () => {
    renderPage();
    expect(
      await screen.findByRole("heading", { level: 1, name: "Seu progresso" })
    ).toBeInTheDocument();
    expect(
      screen.getByText(/Ainda não há atividades respondidas/i)
    ).toBeInTheDocument();
    expect(screen.getByText(/Concluir um módulo não significa domínio/i)).toBeInTheDocument();
  });

  it("lista módulos praticados com etiqueta de domínio", async () => {
    window.localStorage.setItem(
      "aprende-brasil:attempts",
      JSON.stringify([
        { moduleId: "mat-soma", activityId: "a", correct: true, at: 1 },
        { moduleId: "mat-soma", activityId: "b", correct: true, at: 2 },
      ])
    );
    window.localStorage.setItem(
      "aprende-brasil:progress",
      JSON.stringify({ "mat-soma": 100 })
    );
    renderPage();
    expect(await screen.findByText("Somar com as mãos")).toBeInTheDocument();
    expect(screen.getByText("Consolidando")).toBeInTheDocument();
    expect(screen.getByText(/2 tentativas/)).toBeInTheDocument();
  });

  it("mostra pendências de revisão sem inventar número", async () => {
    window.localStorage.setItem(
      "aprende-brasil:reviews",
      JSON.stringify({
        "mat-soma": { repetitions: 1, intervalDays: 1, ease: 2.5, dueAt: 0 },
      })
    );
    renderPage();
    expect(await screen.findByText(/Para revisar/i)).toBeInTheDocument();
  });

  it("apagar dados pede confirmação e limpa o armazenamento", async () => {
    const user = userEvent.setup();
    window.localStorage.setItem("aprende-brasil:progress", JSON.stringify({ a: 1 }));
    renderPage();
    await user.click(
      screen.getByRole("button", { name: /Apagar dados deste navegador/i })
    );
    await waitFor(() => {
      expect(window.localStorage.getItem("aprende-brasil:progress")).toBe("{}");
    });
  });

  it("importar arquivo inválido não quebra a página", async () => {
    const user = userEvent.setup();
    renderPage();
    const input = screen.getByLabelText("Escolher arquivo de progresso");
    const file = new File(["isto não é json"], "ruim.json", {
      type: "application/json",
    });
    await user.upload(input as HTMLInputElement, file);
    expect(
      await screen.findByRole("heading", { level: 1, name: "Seu progresso" })
    ).toBeInTheDocument();
  });
});
