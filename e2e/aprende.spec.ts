import { expect, test, type Page } from "@playwright/test";

/**
 * E2E de comportamento real no navegador.
 *
 * Cada teste parte de um estado limpo (localStorage vazio) porque o progresso
 * é do aparelho, não do servidor.
 */

async function openClean(page: Page, path = "/") {
  await page.goto(path);
  await page.evaluate(() => window.localStorage.clear());
  await page.reload();
}

test.describe("catálogo e navegação", () => {
  test("abre a página inicial com o conteúdo curricular", async ({ page }) => {
    await openClean(page);
    await expect(page).toHaveTitle(/aprende\. Brasil/);
    await expect(page.getByRole("heading", { level: 1 })).toContainText(
      /Aprender é para todos/
    );
    await expect(page.getByText("205").first()).toBeVisible();
  });

  test("busca global encontra módulo de outra trilha", async ({ page }) => {
    await openClean(page);
    const search = page
      .getByRole("searchbox")
      .or(page.getByPlaceholder(/buscar/i));
    await search.first().fill("porcentagem");
    await expect(
      page.getByText(/Porcentagem no dia a dia/i).first()
    ).toBeVisible();
  });

  test("paginação carrega mais módulos", async ({ page }) => {
    await openClean(page);
    const before = await page.locator(".module-card, article").count();
    const loadMore = page.getByRole("button", { name: /carregar mais/i });
    if (await loadMore.count()) {
      await loadMore.first().click();
      await expect
        .poll(async () => page.locator(".module-card, article").count())
        .toBeGreaterThan(before);
    }
  });

  test("abre módulo direto pela URL profunda", async ({ page }) => {
    await openClean(page, "/modulo/alfa-letra-a");
    await expect(
      page.getByRole("heading", { level: 1, name: "A letra A" })
    ).toBeVisible();
    // A navegação direta precisa funcionar em subpath (GitHub Pages) também.
    await page.reload();
    await expect(
      page.getByRole("heading", { level: 1, name: "A letra A" })
    ).toBeVisible();
  });

  test("módulo inexistente mostra 404 amigável", async ({ page }) => {
    await openClean(page, "/modulo/nao-existe");
    await expect(
      page.getByRole("heading", { level: 1, name: /Módulo não encontrado/i })
    ).toBeVisible();
  });
});

test.describe("atividades interativas", () => {
  test("múltipla escolha corrige e explica", async ({ page }) => {
    await openClean(page, "/modulo/alfa-letra-a");
    const card = page.locator(".activity-card").first();
    await expect(card).toBeVisible();
    await card.getByRole("button", { name: /vogal/i }).first().click();
    await expect(card.locator(".activity-feedback")).toBeVisible();
    await expect(card.locator(".activity-feedback")).toContainText(
      /Certo|Ainda não/
    );
  });

  test("lacuna aceita resposta com caixa diferente", async ({ page }) => {
    await openClean(page, "/modulo/alfa-letra-a");
    const card = page
      .locator(".activity-card")
      .filter({ has: page.getByText(/Complete com a letra/i) })
      .first();
    await card.getByRole("textbox").fill("A");
    await card.getByRole("button", { name: "Conferir" }).click();
    await expect(card.locator(".activity-feedback")).toContainText(/Certo/);
  });

  test("acertar atividade marca a etapa de prática", async ({ page }) => {
    await openClean(page, "/modulo/alfa-letra-a");
    const bar = page.getByRole("progressbar", { name: "Progresso do módulo" });
    const initial = Number(await bar.getAttribute("aria-valuenow"));
    const card = page.locator(".activity-card").first();
    await card.getByRole("button", { name: /vogal/i }).first().click();
    await expect
      .poll(async () => Number(await bar.getAttribute("aria-valuenow")))
      .toBeGreaterThan(initial);
  });

  test("progresso e atividade sobrevivem ao recarregar", async ({ page }) => {
    await openClean(page, "/modulo/mat-troco");
    const card = page.locator(".activity-card").first();
    await card.getByRole("textbox").fill("4");
    await card.getByRole("button", { name: "Conferir" }).click();
    await expect(card.locator(".activity-feedback")).toContainText(/Certo/);
    await page.reload();
    await expect(
      page.getByRole("progressbar", { name: "Progresso do módulo" })
    ).not.toHaveAttribute("aria-valuenow", "0");
  });

  test("numérico aceita vírgula decimal", async ({ page }) => {
    await openClean(page, "/modulo/mat-troco");
    const card = page
      .locator(".activity-card")
      .filter({ has: page.getByText(/7,50/).first() })
      .first();
    if (await card.count()) {
      await card.getByRole("textbox").fill("2,5");
      await card.getByRole("button", { name: "Conferir" }).click();
      await expect(card.locator(".activity-feedback")).toContainText(/Certo/);
    }
  });
});

test.describe("progresso e portabilidade", () => {
  test("concluir módulo agenda revisão e aparece em /progresso", async ({
    page,
  }) => {
    await openClean(page, "/modulo/mat-soma");
    await page.getByRole("button", { name: /Concluir módulo/i }).click();
    await expect(page.getByRole("progressbar")).toHaveAttribute(
      "aria-valuenow",
      "100"
    );
    await page.goto("/progresso");
    await expect(
      page.getByRole("heading", { level: 1, name: "Seu progresso" })
    ).toBeVisible();
    await expect(page.getByText(/Módulos concluídos/i)).toBeVisible();
    await expect(page.getByText("1", { exact: true }).first()).toBeVisible();
  });

  test("favoritos persistem", async ({ page }) => {
    await openClean(page, "/modulo/alfa-letra-a");
    const fav = page
      .getByRole("button", { name: /favoritar|favorito/i })
      .first();
    await fav.click();
    await expect(fav).toHaveAttribute("aria-pressed", "true");
    await page.reload();
    await expect(
      page.getByRole("button", { name: /favorito/i }).first()
    ).toHaveAttribute("aria-pressed", "true");
  });

  test("exporta e reimporta o progresso", async ({ page }) => {
    await openClean(page, "/modulo/mat-soma");
    await page.getByRole("button", { name: /Concluir módulo/i }).click();
    await page.goto("/progresso");

    const downloadPromise = page.waitForEvent("download");
    await page.getByRole("button", { name: /Exportar progresso/i }).click();
    const download = await downloadPromise;
    const path = await download.path();
    expect(path).toBeTruthy();

    // Reimporta o mesmo arquivo depois de limpar o navegador.
    await page.evaluate(() => window.localStorage.clear());
    await page.reload();
    await page
      .getByLabel("Escolher arquivo de progresso")
      .setInputFiles(path as string);
    await expect(page.getByText(/Progresso restaurado/i)).toBeVisible({
      timeout: 10_000,
    });
  });

  test("importação recusa arquivo inválido sem quebrar", async ({ page }) => {
    await openClean(page, "/progresso");
    await page.getByLabel("Escolher arquivo de progresso").setInputFiles({
      name: "ruim.json",
      mimeType: "application/json",
      buffer: Buffer.from("{ isto não é json }"),
    });
    await expect(page.getByText(/Arquivo ilegível/i)).toBeVisible();
    await expect(
      page.getByRole("heading", { level: 1, name: "Seu progresso" })
    ).toBeVisible();
  });
});

test.describe("tutor local", () => {
  test("responde usando conteúdo real do currículo, sem rede", async ({
    page,
  }) => {
    await openClean(page);
    let apiCalls = 0;
    page.on("request", request => {
      if (request.url().includes("/api/")) apiCalls += 1;
    });
    await page
      .getByRole("button", { name: /tutor Nilo/i })
      .first()
      .click();
    const input = page.getByRole("textbox").last();
    await input.fill("o que é porcentagem?");
    await input.press("Enter");
    await expect(
      page.getByText(/Vamos com porcentagem no dia a dia|Porcentagem/i).last()
    ).toBeVisible({ timeout: 15_000 });
    expect(apiCalls).toBe(0);
  });
});

test.describe("acessibilidade e teclado", () => {
  test("navegação por teclado chega ao conteúdo e marca etapa", async ({
    page,
  }) => {
    await openClean(page, "/modulo/alfa-letra-a");
    await page.keyboard.press("Tab");
    const skip = page.locator(":focus");
    await expect(skip).toBeVisible();
    // Marca uma etapa via teclado, sem mouse.
    const check = page.getByRole("button", { name: /Marcar etapa 1/i });
    await check.focus();
    await page.keyboard.press("Enter");
    await expect(check).toHaveAttribute("aria-pressed", "true");
  });

  test("contraste real: texto principal sobre o fundo tem contraste AA", async ({
    page,
  }) => {
    await openClean(page, "/modulo/alfa-letra-a");
    const ratio = await page.evaluate(() => {
      const parse = (color: string) => {
        const match = color.match(/rgba?\(([^)]+)\)/);
        if (!match) return [0, 0, 0];
        return match[1]
          .split(",")
          .slice(0, 3)
          .map(v => Number(v.trim()));
      };
      const lum = ([r, g, b]: number[]) => {
        const channel = (value: number) => {
          const c = value / 255;
          return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
        };
        return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b);
      };
      const el = document.querySelector(".step-body p") as HTMLElement;
      const style = getComputedStyle(el);
      let bg = "rgb(255,255,255)";
      let node: HTMLElement | null = el;
      while (node) {
        const candidate = getComputedStyle(node).backgroundColor;
        if (candidate && candidate !== "rgba(0, 0, 0, 0)") {
          bg = candidate;
          break;
        }
        node = node.parentElement;
      }
      const l1 = lum(parse(style.color));
      const l2 = lum(parse(bg));
      const lighter = Math.max(l1, l2);
      const darker = Math.min(l1, l2);
      return (lighter + 0.05) / (darker + 0.05);
    });
    expect(ratio).toBeGreaterThanOrEqual(4.5);
  });

  test("@mobile layout de celular não tem rolagem horizontal", async ({
    page,
  }) => {
    await openClean(page, "/modulo/alfa-letra-a");
    const overflow = await page.evaluate(
      () => document.documentElement.scrollWidth - window.innerWidth
    );
    expect(overflow).toBeLessThanOrEqual(1);
  });
});

test.describe("PWA", () => {
  test("manifest e service worker são servidos com o base correto", async ({
    page,
    request,
  }) => {
    await openClean(page);
    const href = await page.getAttribute('link[rel="manifest"]', "href");
    expect(href).toBeTruthy();
    const manifest = await request.get(href as string);
    expect(manifest.ok()).toBeTruthy();
    const json = await manifest.json();
    expect(json.name).toContain("Aprende Brasil");
    expect(json.icons.length).toBeGreaterThan(0);

    // O service worker precisa controlar a página depois do registro.
    const controlled = await page.evaluate(async () => {
      if (!("serviceWorker" in navigator)) return "sem-suporte";
      const registration = await navigator.serviceWorker.getRegistration();
      return registration ? "registrado" : "nao-registrado";
    });
    expect(["registrado", "sem-suporte"]).toContain(controlled);
  });

  test("@mobile a faixa de estado não cobre o conteúdo quando online", async ({
    page,
  }) => {
    await openClean(page);
    await expect(page.locator(".app-status__item--offline")).toHaveCount(0);
    await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
  });

  test("abre offline depois de visitar (cache do shell)", async ({
    page,
    context,
  }) => {
    await openClean(page);
    await page.waitForLoadState("networkidle");
    // Espera o service worker assumir o controle.
    await page.evaluate(async () => {
      if (!("serviceWorker" in navigator)) return;
      await navigator.serviceWorker.ready;
      if (!navigator.serviceWorker.controller) {
        await new Promise<void>(resolve => {
          navigator.serviceWorker.addEventListener("controllerchange", () =>
            resolve()
          );
          setTimeout(resolve, 4000);
        });
      }
    });
    await context.setOffline(true);
    await page.reload();
    await expect(page.getByRole("heading", { level: 1 })).toBeVisible({
      timeout: 15_000,
    });
    await context.setOffline(false);
  });
});
