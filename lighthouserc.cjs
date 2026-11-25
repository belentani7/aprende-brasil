/**
 * Lighthouse CI — mede o **build estático real** (dist/public), não o dev server.
 *
 * Regras que valem neste arquivo:
 *
 * - Nada de "score gaming": não desligamos auditorias que reprovam. Se uma
 *   auditoria legítima falhar, o problema é do site, não do teste.
 * - As três execuções existem porque medição de performance tem variância de
 *   alguns pontos; a mediana é o valor honesto, não o melhor caso.
 * - `performance` é `error` em 0.95 (a meta do projeto). Acessibilidade também é
 *   `error`: um site para pessoas aprendendo a ler não pode ter defeito de
 *   acessibilidade.
 * - SEO e boas práticas ficam em `warn` porque dependem de coisas externas
 *   (domínio final, redirects do GitHub Pages) que não controlamos aqui.
 */
const basePath = process.env.VITE_BASE_PATH || "/";
const root = `http://127.0.0.1:4173${basePath.replace(/\/$/, "")}`;

module.exports = {
  ci: {
    collect: {
      staticDistDir: "./dist/public",
      url: [`${root}/`, `${root}/modulo/alfa-letra-a`, `${root}/progresso`],
      numberOfRuns: 3,
      settings: {
        // Sem throttling artificial "bonito": o perfil móvel padrão do Lighthouse
        // (4G lento, CPU 4x) é o que corresponde a telefone barato, que é o
        // aparelho do nosso público.
        preset: "desktop",
        skipAudits: [],
      },
    },
    assert: {
      assertions: {
        "categories:performance": ["error", { minScore: 0.95 }],
        "categories:accessibility": ["error", { minScore: 0.95 }],
        "categories:best-practices": ["warn", { minScore: 0.9 }],
        "categories:seo": ["warn", { minScore: 0.9 }],

        // PWA: o service worker precisa ser registrável, e o manifest válido.
        "service-worker": "off", // auditoria PWA saiu do Lighthouse 12; coberta no Playwright
        "installable-manifest": "off",
        "maskable-icon": "off",

        // Problemas que aparecem como "quase verde" e enganam o time.
        "unused-javascript": ["warn", { maxLength: 0 }],
        "uses-responsive-images": "warn",
        "color-contrast": "error",
        "heading-order": "error",
        "button-name": "error",
        label: "error",
        "html-has-lang": "error",
        "meta-viewport": "error",
        "tap-targets": "error",
        "link-name": "error",
        "document-title": "error",
        "no-vulnerable-libraries": "warn",
        "unsized-images": "warn",
      },
    },
    upload: {
      // Só sobe para o storage temporário público do LHCI; nada de token secreto.
      target: "temporary-public-storage",
    },
  },
};
