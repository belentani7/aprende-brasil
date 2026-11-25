# E2E com navegador real

Testes de ponta a ponta em **Chromium real** contra o build estático servido por
`vite preview`. Complementam o Vitest (JSDOM) justamente onde o JSDOM não chega:
CSS e contraste calculados, service worker, navegação real, download de arquivo
e viewport de celular.

```bash
npm run build                 # o preview serve dist/public
npx playwright install --with-deps chromium

npm run test:e2e              # base "/"
npm run test:e2e:pages        # base "/aprende-brasil/" (GitHub Pages)
```

## O que é verificado

| Área | Teste |
| --- | --- |
| Catálogo | título, total de módulos, busca global, paginação |
| Rotas | abertura direta de `/modulo/:id` (com reload), 404 amigável |
| Atividades | múltipla escolha, lacuna com caixa diferente, numérica com vírgula |
| Progresso | acertar atividade marca etapa, persistência após reload |
| Portabilidade | exportar baixa o JSON e importar restaura; arquivo inválido é recusado |
| Favoritos | `aria-pressed` persiste após reload |
| Tutor | responde sem nenhuma chamada a `/api/` |
| Teclado | skip link recebe foco, etapa é marcada com Enter |
| Contraste | razão calculada no navegador ≥ 4.5 no texto principal |
| Mobile | sem rolagem horizontal em viewport de Pixel 5 |
| PWA | manifest servido com o base correto, SW registrado, abre offline |

## Por que estes testes não rodam em todo PR local

O Chromium não está disponível no ambiente de desenvolvimento usado para gerar o
conteúdo (o download é bloqueado). Por isso o README não reporta números de
Lighthouse: eles são coletados apenas no workflow `e2e.yml`, no GitHub Actions,
onde o navegador existe.

Se um teste falhar no CI, o relatório HTML fica no artifact `playwright-report`.

## Convenções

- `@mobile` no nome do teste faz ele rodar também no projeto `mobile`.
- Cada teste limpa o `localStorage` antes de começar (o progresso é do
  aparelho, não do servidor).
- Nunca use `page.waitForTimeout`: prefira `expect(...).toHaveAttribute` e
  `expect.poll`, que falham rápido e não dependem de tempo fixo.
