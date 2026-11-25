# Aprende Brasil

Plataforma de **alfabetização e educação aberta** em português brasileiro para
quem não teve acesso à escola — e para qualquer grupo que queira se organizar
como uma **instituição mínima**: sem matrícula, sem dados pessoais e sem
publicidade.

O conteúdo é escrito e revisado em português (não é tradução automática), mora
em SQLite e é exportado para JSON. O site é **100% estático**: o progresso e os
favoritos ficam no `localStorage` do navegador.

## O que está pronto

- **205 módulos** com 5 etapas cada (entender → exemplo → praticar → verificar →
  próximo passo): **1.025 etapas** no total.
  - Alfabetização: **93** módulos com palavras e textos reais do dia a dia.
  - Informática: **40** módulos.
  - Matemática: **40** módulos.
  - Idiomas: **32** módulos.
- **Painel do estudante** com trilhas, catálogo paginado, busca em todas as
  trilhas, progresso por módulo, atividade real dos últimos 7 dias e sequência
  de estudo.
- **Página de leção** (`/modulo/:id`): cinco etapas, marcação com progresso
  persistente, favoritos e leitura em voz alta (pt-BR) do próprio navegador.
- **Tutor Nilo** com motor local offline e LLM opcional no backend.
- **Acessibilidade**: link para saltar ao conteúdo, diálogo com foco preso e
  fechamento por `Esc`, `aria-current`, `aria-pressed`, barras de progresso com
  valor acessível, textos alternativos, `prefers-reduced-motion` respeitado e
  zoom liberado no viewport.

## Stack

| Camada           | Tecnologia                                                    |
| ---------------- | ------------------------------------------------------------- |
| Experiência      | React 19, Vite 7, TailwindCSS 4, wouter, sonner, lucide-react |
| Tipografia       | DM Sans, Syne e DM Mono **auto-hospedadas** (`@fontsource`)   |
| Dados no cliente | `client/src/data/*.json` + `localStorage`                     |
| Conteúdo         | SQLite (`data/aprende.db`) + scripts Python 3                 |
| API opcional     | FastAPI + SQLAlchemy (Python 3.11+)                           |
| Testes           | Vitest + Testing Library (frontend) e pytest (API/dados)      |

Sem framework de UI de terceiros no bundle: os estilos vivem em
`client/src/index.css` (custom properties, grid e flex), e o único componente
externo é o toast (`sonner`).

## Arquitetura

```
client/                  frontend React
  src/data/
    curriculum.json      catálogo: 4 trilhas + 205 módulos (≈56 KB)
    curriculum-steps.json 1.025 etapas (≈183 KB) — download sob demanda
  public/open-data/      dados abertos servidos como arquivos estáticos
api/                     backend FastAPI opcional (dev e tutor com LLM)
scripts/                 geração e exportação do currículo
  content_*.py           conteúdo curado por trilha
  build_curriculum.py    popula data/aprende.db
  export_static_curriculum.py  exporta os dois JSON (stdlib, sem rede)
  build-curriculum.mjs   orquestra o export no npm (fallback sem Python)
tools/aprende.mjs        CLI interna: stats, validate, budget
data/aprende.db          fonte de verdade do currículo
tests/                   pytest: API, integridade dos dados e qualidade do texto
functions/               Pages Function (fallback SPA na Cloudflare)
dist/public              build estático
```

### Por que dois arquivos de currículo

A primeira visita só precisa do catálogo. As 1.025 etapas somam a maior parte
dos bytes, então vivem em um chunk separado, carregado quando a pessoa abre um
módulo ou usa o tutor. O JavaScript inicial fica em **≈106 KB gzip**; o chunk
de etapas (**≈34 KB gzip**) só é baixado quando necessário.

As rotas `/modulo/:id`, `/sobre` e o 404 também são `import()` dinâmicos, e o
motor do tutor é carregado na primeira pergunta.

## Rodar

Requisitos: **Node 22+**, **npm 10+** e, para regenerar conteúdo, **Python 3.11+**.

```bash
npm install            # dependências do frontend
npm run dev            # Vite em http://localhost:5173
```

O currículo já está versionado. Para gerar do zero:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt

npm run seed           # baixa dados abertos + reconstrói data/aprende.db
npm run curriculum     # exporta client/src/data/*.json
```

Build de produção e API opcional:

```bash
npm run build          # dist/public
npm run preview        # serve o build em http://localhost:4173

npm run dev:api        # FastAPI em http://localhost:8000 (tutor com LLM)
```

## Scripts

| Comando                    | O que faz                                                      |
| -------------------------- | -------------------------------------------------------------- |
| `npm run dev`              | Vite com recarregamento; gera o currículo antes                |
| `npm run build`            | Exporta o currículo, compila e cria o `404.html`               |
| `npm run check`            | Typecheck (`tsc --noEmit`)                                     |
| `npm test`                 | Vitest (52 testes: dados, tutor, progresso, componentes, a11y) |
| `npm run test:py`          | pytest (42 testes: API, dados, exportação, conteúdo)           |
| `npm run verify`           | check + testes + build + orçamento                             |
| `npm run audit`            | Valida o contrato dos dados e o orçamento de bundle            |
| `npm run stats`            | Números do currículo por trilha e tipo de etapa                |
| `npm run curriculum:check` | Falha se os JSON não baterem com o SQLite                      |
| `npm run format`           | Prettier em todo o projeto                                     |

### CLI interna

```bash
node tools/aprende.mjs --help
node tools/aprende.mjs stats
node tools/aprende.mjs validate   # sai com 1 se o currículo quebrar o contrato
node tools/aprende.mjs budget     # falha acima de 120 KiB de JS inicial (gzip)
```

O orçamento atual está em `tools/aprende.mjs`. Aumentar um limite exige
justificativa no PR.

## Testes

**Frontend (Vitest + jsdom + Testing Library)**

- integridade do catálogo e das 1.025 etapas (ordem, tipos, texto mínimo);
- paginação, busca global, destaques e resolução de módulo;
- progresso monotônico, etapas concluídas, atividade diária e favoritos;
- tolerância a `localStorage` corrompido;
- painel: carregar mais, buscar, abrir diálogo e fechar com `Esc`;
- leção: restaurar progresso, marcar etapa, concluir e tratar módulo inexistente;
- foco preso no diálogo e devolução de foco;
- motor do tutor (9 cenários de intenção) e semana de atividade;
- auditoria axe-core (WCAG A/AA) no painel, na leção e na página institucional.

**Python (pytest)**

- API endpoint a endpoint com SQLite isolado por teste;
- 205 módulos, 1.025 etapas, 5 etapas na ordem e ids únicos;
- JSON exportado idêntico ao banco, inclusive os textos;
- qualidade editorial: sem placeholders, palavras curadas em cada módulo de
  letra/família/tema e exemplos reais nos textos do dia a dia.

## Deploy

O site é estático. O backend não é necessário em produção.

| Host             | Configuração                                                         |
| ---------------- | -------------------------------------------------------------------- |
| Vercel           | `vercel.json` → `npm ci`, `npm run build`, `dist/public`             |
| Netlify          | `netlify.toml` → `npm run build`, `dist/public`                      |
| Cloudflare Pages | build `npm run build`, saída `dist/public`, `functions/[[path]].js`  |
| GitHub Pages     | publicar `dist/public`; use `--base=/aprende-brasil/` para o subpath |

Notas de campo que custaram tempo:

- **Vercel**: `requirements.txt` na raiz faz o builder tentar compilar
  `pydantic-core` e o build morre; por isso existe `.vercelignore`. As regras
  são ancoradas em `/` para não excluir `client/src/data/`. Como `/data/` fica
  fora do deploy, o `prebuild` detecta a ausência do SQLite e usa os JSON já
  versionados (e falha se eles não existirem).
- **Cloudflare Pages**: `_redirects` tem prioridade sobre assets estáticos e um
  catch-all serve `/assets/*.js` como `text/html`; o fallback correto é a Pages
  Function em `functions/`.
- **GitHub Pages**: serve em subpath, então o build precisa de
  `--base=/aprende-brasil/` **e** o `WouterRouter` usa `import.meta.env.BASE_URL`.
  O fallback é o `404.html` gerado no postbuild.

## Dados e privacidade

- Não há cadastro, login, cookies de rastreamento ou analytics.
- Progresso, etapas concluídas, atividade e favoritos ficam no `localStorage`,
  sob as chaves `aprende-brasil:*`. Limpar os dados do site apaga o progresso.
- A leitura em voz alta usa a síntese do próprio navegador; nenhum áudio sai do
  dispositivo.
- O tutor local funciona sem rede. Com `VITE_API_URL` definido, o cliente tenta
  o backend e cai para o motor local se ele não responder.

## API opcional

| Método       | Rota                                | Descrição                     |
| ------------ | ----------------------------------- | ----------------------------- |
| `GET`        | `/api/health`                       | status                        |
| `GET`        | `/api/tracks`                       | trilhas + contagem de módulos |
| `GET`        | `/api/modules?track=&search=&page=` | catálogo paginado             |
| `GET`        | `/api/modules/featured`             | destaques                     |
| `GET`        | `/api/modules/{id}`                 | módulo + etapas               |
| `POST`       | `/api/tutor/ask`                    | tutor Nilo                    |
| `GET`/`POST` | `/api/progress`                     | progresso por módulo          |
| `GET`/`POST` | `/api/favorites`                    | favoritos (toggle)            |
| `GET`        | `/api/stats`                        | resumo do usuário             |

Configuração do LLM (somente no backend):

```
LLM_API_URL=https://api.exemplo.com/v1/chat/completions
LLM_API_KEY=...
LLM_MODEL=gpt-4o-mini
```

## Qualidade medida

Medido neste repositório com `npm run build && npm run audit`:

| Métrica             | Valor                      |
| ------------------- | -------------------------- |
| JS inicial          | ≈106 KiB gzip              |
| CSS                 | ≈10,4 KiB gzip             |
| Bundle total (dist) | ≈803 KiB em disco          |
| Testes              | 52 Vitest + 42 pytest (94) |
| Typecheck           | limpo (`strict: true`)     |

Lighthouse não é executado no CI porque o runner não traz um Chrome
controlável; o orçamento de bundle é a regressão automatizada de performance.

## Próximos passos

- Exercícios com correção automática (hoje a verificação é autoavaliação).
- Importador versionado de módulos + revisão editorial com histórico.
- Metas e agenda persistidas por semana.
- Revisão WCAG 2.2 AA com usuários reais e testes com leitor de tela.
- Áudio pré-gravado para conexões lentas, além da síntese do navegador.

## Licença

MIT. Conteúdo pedagógico escrito para este projeto; dados abertos citados em
`client/public/open-data/README.md`.

---

## Parte do índice educativo

Esta plataforma forma parte do conjunto educativo de **Belentani / NOIACORE**:
formação gratuita e aberta. O índice completo vive em
<https://github.com/belentani7/open-school/blob/main/INDICE-EDUCATIVO.md>.

**PT > ES > EN > CA.** Gratuito, acessível (WCAG) e conectado.
