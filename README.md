# Aprende Brasil

Plataforma de **alfabetização e educação aberta** em português brasileiro, para
quem não teve acesso à escola e para qualquer grupo que queira se organizar como
uma **instituição mínima** — sem matrícula, sem dados pessoais, sem publicidade.

O conteúdo é gerado a partir de **bancos de dados abertos** por scripts Python,
e a plataforma roda **standalone**: frontend React + API FastAPI + SQLite.

## O que está pronto

- **205 módulos** com 5 etapas pedagógicas cada (entender → exemplo → praticar →
  verificar → próximo passo): 93 de Alfabetização, 40 de Informática, 40 de
  Matemática e 32 de Idiomas.
- **Trilha de Alfabetização real**: letras, famílias silábicas, temas de
  vocabulário, frases e textos do dia a dia (conta de luz, bula, formulário…).
- **Dashboard** do estudante: trilhas, catálogo com busca, módulos em destaque,
  agenda e tutor.
- **Vista de leção** (`/modulo/:id`): passo a passo, progresso salvo, favoritos
  e leitura em voz alta (pt-BR) no navegador.
- **Tutor Nilo** com LLM opcional (OpenAI-compatível) e fallback local offline.
- **API de progresso e favoritos** por usuário.

## Arquitetura

| Camada | Tecnologia |
| --- | --- |
| Experiência | React 19 + Vite + TailwindCSS 4 + shadcn/ui + wouter |
| Dados no cliente | `client/src/data/curriculum.json` (205 módulos) + `localStorage` |
| Conteúdo | Scripts Python: banco de palavras aberto + conteúdo curado |
| API (opcional) | FastAPI + SQLAlchemy (Python 3.11+) — só dev/tutor com LLM |
| Fonte | SQLite (`data/aprende.db`) |

```
client/     frontend React (lib/api.ts, lib/tutor.ts, data/curriculum.json)
api/        backend FastAPI (opcional — dev e tutor com LLM)
scripts/    fetch_open_data.py, build_curriculum.py, export_curriculum.py, content_*.py
data/       aprende.db + open/palavras-pt.txt
functions/  Pages Function (fallback SPA da Cloudflare)
dist/public build do frontend (vite build)
```

## Rodar

```bash
# 1. dependências
pnpm install
pip install -r requirements.txt

# 2. dados: baixa o banco aberto e gera o currículo
pnpm seed            # = python -m scripts.fetch_open_data && python -m scripts.build_curriculum

# 3. desenvolvimento (duas terminais)
pnpm dev             # Vite em :5173 (proxy /api -> :8000)
pnpm dev:api         # FastAPI em :8000

# 4. produção (um só serviço: FastAPI serve o SPA compilado)
pnpm build           # gera dist/public
pnpm start           # uvicorn em :8000 servindo dist/public
```

## Testes

Suíte Python (pytest) que valida a API endpoint a endpoint e a integridade do
currículo em `data/aprende.db`:

```bash
pip install -r requirements-dev.txt
pnpm test:py          # = python -m pytest
```

Cobre: health, trilhas, catálogo (paginação, busca, filtro por trilha),
módulo + etapas ordenadas, 404 de módulo inexistente, tutor (fallback local),
progresso (monotônico), estatísticas e favoritos — mais 6 checagens de dados
(205 módulos, 1025 etapas, 5 etapas na ordem certa por módulo, `content_json`
válido, ids únicos, nenhuma trilha órfã).

## Ao vivo

| Host | URL | Status |
| --- | --- | --- |
| Cloudflare Pages | https://aprende-brasil-5gq.pages.dev | ✅ |
| Vercel | https://aprende-brasil-belentani7pedro-6758s-projects.vercel.app | ✅ |
| GitHub Pages | https://belentani7.github.io/aprende-brasil/ | ✅ (rotas SPA respondem 404 + app) |

O site é **100% estático**: o currículo viaja como JSON (`client/src/data/curriculum.json`)
e o progresso/favoritos ficam no `localStorage` do navegador. Não há backend em produção.

## API

A plataforma **não precisa de servidor**: `client/src/lib/api.ts` lê o JSON local e o
`localStorage`. O FastAPI (`api/`) segue disponível para uso local/dev e para servir o
tutor com LLM — basta definir `VITE_API_URL` no build para o cliente preferir o backend.

| Método | Rota | Descrição |
| --- | --- | --- |
| `GET` | `/api/health` | status |
| `GET` | `/api/tracks` | trilhas + contagem de módulos |
| `GET` | `/api/modules?track=&search=&page=` | catálogo paginado |
| `GET` | `/api/modules/featured` | destaques |
| `GET` | `/api/modules/{id}` | módulo + etapas |
| `POST` | `/api/tutor/ask` | tutor Nilo |
| `GET`/`POST` | `/api/progress` | progresso por módulo |
| `GET`/`POST` | `/api/favorites` | favoritos (toggle) |
| `GET` | `/api/stats` | resumo do usuário |

## Tutor Nilo (offline)

Sem backend, o tutor responde com um motor local em `client/src/lib/tutor.ts`: ele
detecta a intenção da pergunta, busca no currículo os módulos mais relevantes e compõe
uma resposta ampla — conceito, exemplo concreto, prática, verificação e próximo passo —
sempre citando conteúdo real dos 205 módulos.

Para usar um LLM, defina as variáveis no backend e aponte o cliente para ele:

```
VITE_API_URL=https://seu-backend        # build do cliente
LLM_API_URL=https://api.exemplo.com/v1/chat/completions
LLM_API_KEY=...
LLM_MODEL=gpt-4o-mini
```

## Bancos de dados abertos

- **Lista de palavras do português** — [pythonprobr/palavras](https://github.com/pythonprobr/palavras) (MIT),
  baixada e normalizada por `scripts/fetch_open_data.py` em `data/open/palavras-pt.txt`.
- O currículo é construído por `scripts/build_curriculum.py` a partir dessa base
  e de listas curadas (informática, matemática, idiomas).

Os scripts usam **apenas a biblioteca padrão** para o download.

## Deploy

Tudo é estático, então qualquer CDN serve. O que cada host precisa:

| Host | Comando | Fallback SPA |
| --- | --- | --- |
| Cloudflare Pages | `wrangler pages deploy dist/public --project-name aprende-brasil` | `functions/[[path]].js` |
| Vercel | `vercel deploy --prod` | `rewrites` em `vercel.json` |
| Netlify | `netlify deploy --prod --dir=dist/public` | `netlify.toml` |
| GitHub Pages | publicar `dist/public` na branch `gh-pages` | `404.html` + `.nojekyll` |

Notas de campo (custaram tempo, ficam registradas):

- **Vercel**: `requirements.txt` na raiz faz a Vercel tentar compilar `pydantic-core`
  e o build morre. Por isso existe `.vercelignore` — as regras são ancoradas em `/`
  (`/data/`, não `data/`), senão `client/src/data/curriculum.json` também é excluído.
- **Cloudflare Pages**: `_redirects` tem prioridade **sobre** os assets estáticos, e um
  catch-all `/*` serve `/assets/*.js` como `text/html`. Por isso o fallback é uma
  Pages Function, que só cai no `index.html` quando o asset realmente não existe.
- **GitHub Pages**: serve em subpath, então o build precisa de `--base=/aprende-brasil/`
  **e** o `WouterRouter` precisa de `base` (em `client/src/App.tsx`), senão as rotas
  caem no NotFound. Como Pages não tem rewrites, o fallback é o `404.html` — as rotas
  SPA respondem com status 404 mas entregam a app e funcionam.
- **Deployment Protection** na Vercel bloqueia o site público (302 para SSO). Desative
  com `ssoProtection: null` via API do projeto.

## Próximos passos

- Exercícios com correção automática (hoje o "check" é autoavaliação).
- Importador de módulos versionado + revisão editorial.
- Perfis de docente/editor, metas e agenda persistidas.
- Voz (OpenVoice/TTS) atrás de um adaptador server-side.
- Revisão WCAG 2.2 AA com usuários reais.

## Licença

MIT.
