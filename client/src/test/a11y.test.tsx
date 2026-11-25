import axe from "axe-core";
import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { Route, Router } from "wouter";
import { memoryLocation } from "wouter/memory-location";
import Home from "@/pages/Home";
import Modulo from "@/pages/Modulo";
import Sobre from "@/pages/Sobre";

vi.mock("sonner", () => ({
  toast: Object.assign(vi.fn(), {
    success: vi.fn(),
    error: vi.fn(),
    info: vi.fn(),
  }),
  Toaster: () => null,
}));

/** jsdom não calcula layout/contraste; as regras visuais ficam para auditoria manual. */
const IGNORED = new Set(["color-contrast", "landmark-unique"]);

async function violations(container: HTMLElement) {
  const results = await axe.run(container, {
    runOnly: { type: "tag", values: ["wcag2a", "wcag2aa", "best-practice"] },
    rules: Object.fromEntries(
      [...IGNORED].map(rule => [rule, { enabled: false }])
    ),
  });
  return results.violations.map(violation => ({
    id: violation.id,
    nodes: violation.nodes.map(node => node.target.join(" ")),
  }));
}

describe("acessibilidade automatizada (axe-core)", () => {
  it("painel inicial não tem violações WCAG A/AA detectáveis", async () => {
    const { hook } = memoryLocation({ path: "/", record: true });
    const { container } = render(
      <Router hook={hook}>
        <Home />
      </Router>
    );
    await screen.findByText("A letra A");
    expect(await violations(container)).toEqual([]);
  }, 20000);

  it("página de leção não tem violações WCAG A/AA detectáveis", async () => {
    const { hook } = memoryLocation({
      path: "/modulo/alfa-letra-a",
      record: true,
    });
    const { container } = render(
      <Router hook={hook}>
        <Route path="/modulo/:id" component={Modulo} />
      </Router>
    );
    // Espera o conteúdo do módulo aparecer antes de auditar.
    await screen.findByRole("heading", { level: 1, name: "A letra A" });
    expect(await violations(container)).toEqual([]);
  }, 20000);

  it("página institucional não tem violações WCAG A/AA detectáveis", async () => {
    const { hook } = memoryLocation({ path: "/sobre", record: true });
    const { container } = render(
      <Router hook={hook}>
        <Sobre />
      </Router>
    );
    expect(await violations(container)).toEqual([]);
  }, 20000);
});
