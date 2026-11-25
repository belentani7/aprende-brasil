import { describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Route, Router } from "wouter";
import { memoryLocation } from "wouter/memory-location";
import Modulo from "./Modulo";

const toastSuccess = vi.fn();
vi.mock("sonner", () => ({
  toast: Object.assign(vi.fn(), {
    success: (...args: unknown[]) => toastSuccess(...args),
    error: vi.fn(),
    info: vi.fn(),
  }),
}));

function renderModulo(path = "/modulo/alfa-letra-a") {
  const { hook } = memoryLocation({ path, record: true });
  return render(
    <Router hook={hook}>
      <Route path="/modulo/:id" component={Modulo} />
    </Router>
  );
}

describe("página do módulo", () => {
  it("carrega o conteúdo real e as cinco etapas", async () => {
    renderModulo();
    expect(
      await screen.findByRole("heading", { level: 1, name: "A letra A" })
    ).toBeInTheDocument();
    expect(
      screen
        .getAllByRole("listitem")
        .filter(item => item.classList.contains("modulo-step"))
    ).toHaveLength(5);
    expect(screen.getByText(/Leia devagar, em voz alta/)).toBeInTheDocument();
  });

  it("restaura etapas marcadas e o percentual salvo", async () => {
    window.localStorage.setItem(
      "aprende-brasil:progress",
      JSON.stringify({ "alfa-letra-a": 60 })
    );
    window.localStorage.setItem(
      "aprende-brasil:completed-steps",
      JSON.stringify({ "alfa-letra-a": [1, 2, 3] })
    );
    renderModulo();
    const bar = await screen.findByRole("progressbar", {
      name: "Progresso do módulo",
    });
    expect(bar).toHaveAttribute("aria-valuenow", "60");
    const pressed = screen.getAllByRole("button", { pressed: true });
    expect(
      pressed.filter(b => b.classList.contains("step-check"))
    ).toHaveLength(3);
  });

  it("marca uma etapa, persiste e atualiza o progresso", async () => {
    window.localStorage.setItem(
      "aprende-brasil:progress",
      JSON.stringify({ "alfa-letra-a": 40 })
    );
    window.localStorage.setItem(
      "aprende-brasil:completed-steps",
      JSON.stringify({ "alfa-letra-a": [1, 2] })
    );
    const user = userEvent.setup();
    renderModulo();
    await screen.findByRole("heading", { level: 1, name: "A letra A" });
    await user.click(screen.getByRole("button", { name: /Marcar etapa 3/ }));
    await waitFor(() => {
      expect(
        screen.getByRole("progressbar", { name: "Progresso do módulo" })
      ).toHaveAttribute("aria-valuenow", "60");
    });
    const stored = JSON.parse(
      window.localStorage.getItem("aprende-brasil:completed-steps") ?? "{}"
    );
    expect(stored["alfa-letra-a"]).toEqual([1, 2, 3]);
  });

  it("conclui o módulo com um clique", async () => {
    const user = userEvent.setup();
    renderModulo();
    await screen.findByRole("heading", { level: 1, name: "A letra A" });
    await user.click(screen.getByRole("button", { name: /Concluir módulo/i }));
    await waitFor(() => {
      expect(
        screen.getByRole("progressbar", { name: "Progresso do módulo" })
      ).toHaveAttribute("aria-valuenow", "100");
    });
    // A conclusão agora agenda a revisão espaçada e diz quando o módulo volta.
    expect(toastSuccess).toHaveBeenCalledWith("Módulo concluído!", {
      description: expect.stringMatching(/Revisão marcada para/),
    });
    const reviews = JSON.parse(
      window.localStorage.getItem("aprende-brasil:reviews") ?? "{}"
    );
    expect(reviews["alfa-letra-a"]?.repetitions).toBeGreaterThan(0);
  });

  it("mostra estado de erro para módulo inexistente", async () => {
    renderModulo("/modulo/nao-existe");
    expect(
      await screen.findByRole("heading", {
        level: 1,
        name: "Módulo não encontrado",
      })
    ).toBeInTheDocument();
  });
});
