import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Router } from "wouter";
import { memoryLocation } from "wouter/memory-location";
import Home from "./Home";

vi.mock("sonner", () => ({
  toast: Object.assign(vi.fn(), {
    success: vi.fn(),
    error: vi.fn(),
    info: vi.fn(),
  }),
  Toaster: () => null,
}));

function renderHome(path = "/") {
  const { hook } = memoryLocation({ path, record: true });
  return render(
    <Router hook={hook}>
      <Home />
    </Router>
  );
}

describe("painel inicial", () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it("mostra as trilhas e os primeiros vinte módulos", async () => {
    renderHome();
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(
      "Aprender é para todos"
    );
    expect(await screen.findByText("A letra A")).toBeInTheDocument();
    expect(screen.getByText("Mostrando 20 de 93 módulos")).toBeInTheDocument();
    expect(screen.getAllByRole("progressbar").length).toBeGreaterThanOrEqual(4);
  });

  it("carrega mais módulos sob demanda", async () => {
    const user = userEvent.setup();
    renderHome();
    await screen.findByText("A letra A");
    await user.click(
      screen.getByRole("button", { name: /Carregar mais módulos/i })
    );
    await waitFor(() => {
      expect(
        screen.getByText("Mostrando 40 de 93 módulos")
      ).toBeInTheDocument();
    });
  });

  it("busca em todas as trilhas", async () => {
    const user = userEvent.setup();
    renderHome();
    await screen.findByText("A letra A");
    await user.type(
      screen.getByRole("searchbox", { name: /Buscar módulo/i }),
      "porcentagem"
    );
    expect(
      await screen.findByText("Porcentagem no dia a dia")
    ).toBeInTheDocument();
    expect(screen.getByText("Mostrando 1 de 1 módulo")).toBeInTheDocument();
  });

  it("abre os detalhes em um diálogo acessível e fecha com Escape", async () => {
    const user = userEvent.setup();
    renderHome();
    await user.click(await screen.findByRole("button", { name: "A letra A" }));
    const dialog = screen.getByRole("dialog");
    expect(
      within(dialog).getByRole("heading", { name: "A letra A" })
    ).toBeInTheDocument();
    await user.keyboard("{Escape}");
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("mostra o progresso salvo no navegador", async () => {
    window.localStorage.setItem(
      "aprende-brasil:progress",
      JSON.stringify({ "alfa-letra-a": 60 })
    );
    renderHome();
    expect(
      await screen.findByRole("progressbar", { name: "Progresso em A letra A" })
    ).toHaveAttribute("aria-valuenow", "60");
  });
});
