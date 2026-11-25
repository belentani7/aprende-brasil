import { useState } from "react";
import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useDialogA11y } from "./useDialogA11y";

function Demo() {
  const [open, setOpen] = useState(false);
  const ref = useDialogA11y<HTMLDivElement>(open, () => setOpen(false));
  return (
    <div>
      <button onClick={() => setOpen(true)}>Abrir</button>
      <button>Fora</button>
      {open && (
        <div role="dialog" aria-label="Exemplo" ref={ref}>
          <button>Primeiro</button>
          <button>Último</button>
        </div>
      )}
    </div>
  );
}

describe("useDialogA11y", () => {
  it("foca o primeiro controle ao abrir e devolve o foco ao fechar", async () => {
    const user = userEvent.setup();
    render(<Demo />);
    const trigger = screen.getByRole("button", { name: "Abrir" });
    await user.click(trigger);
    expect(screen.getByRole("button", { name: "Primeiro" })).toHaveFocus();
    await user.keyboard("{Escape}");
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    expect(trigger).toHaveFocus();
  });

  it("mantém o Tab dentro do diálogo", async () => {
    const user = userEvent.setup();
    render(<Demo />);
    await user.click(screen.getByRole("button", { name: "Abrir" }));
    await user.tab();
    await user.tab();
    expect(screen.getByRole("button", { name: "Primeiro" })).toHaveFocus();
    await user.tab({ shift: true });
    expect(screen.getByRole("button", { name: "Último" })).toHaveFocus();
  });

  it("fecha com Escape e libera a rolagem do corpo", async () => {
    const user = userEvent.setup();
    render(<Demo />);
    await user.click(screen.getByRole("button", { name: "Abrir" }));
    expect(document.body.style.overflow).toBe("hidden");
    await user.keyboard("{Escape}");
    expect(document.body.style.overflow).toBe("");
  });
});
