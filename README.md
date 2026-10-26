# Aprende Brasil

Plataforma de **alfabetização e educação aberta** em português brasileiro, para
quem não teve acesso à escola e para qualquer grupo que queira se organizar como
uma **instituição mínima** — sem matrícula, sem dados pessoais, sem publicidade.

O conteúdo é gerado a partir de **bancos de dados abertos** por scripts Python,
e a plataforma roda **standalone**: frontend React estático — o progresso e os favoritos ficam no `localStorage` do navegador.

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
| API | ⚠️ o código FastAPI (`api/`) **não está neste repositório** — os scripts que o referenciam (`dev:api`, `start`) falham até ser restaurado |
| Fonte | SQLite (`data/aprende.db`) — presente, consumido pelos scripts Python |

```
client/     frontend React (lib/api.ts, lib/tutor.ts, data/curriculum.json)
api/        backend FastAPI — AUSENTE do repositório (contrato em `## API`, código não commitado)
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

# 2. dados
# ⚠️ NÃO rode `pnpm seed` neste repositório: ele regenera um esqueleto de 10 módulos
#    e SOBRESCREVE o currículo curado de 205 módulos (client/src/data/curriculum.json).
python -m scripts.export_curriculum  # exporta o currículo do SQLite para o JSON estático

# 3. desenvolvimento
pnpm dev             # Vite em :5173 (o site funciona 100% estático, sem API)
# pnpm dev:api       # NÃO DISPONÍVEL: api/ não está no repositório

# 4. build de produção (estático)
pnpm build           # gera dist/public
# pnpm start         # NÃO DISPONÍVEL: depende de api/
```

## Testes

Testes reais no repositório (JavaScript):

```bash
pnpm test             # vitest
pnpm test:privacy     # garante que nenhum coletor de dados entra no build
```

O projeto também tem uma suíte pytest planejada (health, trilhas, catálogo,
progresso, favoritos e 6 checagens de dados do currículo), mas ela valida a API
FastAPI e `pnpm test:py` falha enquanto `api/` não estiver no repositório.

## Ao vivo

| Host | URL | Status |
| --- | --- | --- |
| Cloudflare Pages | https://aprende-brasil-5gq.pages.dev | ✅ |
| Vercel | https://aprende-brasil.vercel.app/ | ✅ |
| GitHub Pages | no publicado — Pages está desactivado en repositorios privados | ❌ |

O site é **100% estático**: o currículo viaja como JSON (`client/src/data/curriculum.json`)
e o progresso/favoritos ficam no `localStorage` do navegador. Não há backend em produção.

## API

A plataforma **não precisa de servidor**: `client/src/lib/api.ts` lê o JSON local e o
`localStorage`. A tabela abaixo é o contrato de rotas desenhado para o backend FastAPI
(com tutor LLM); o código dele não está neste repositório — defina `VITE_API_URL` no
build apenas quando ele existir e estiver no ar.

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

- **Lista de palavras do português** — baseada em [pythonprobr/palavras](https://github.com/pythonprobr/palavras) (MIT).
  `data/open/palavras-pt.txt` está commitado no repositório; hoje **nenhum script baixa** essa lista automaticamente.
- `scripts/fetch_open_data.py` grava JSONs de demonstração em `open-data/` (temas de
  ciência, cultura, vocabulário…). O frontend não consome esse diretório — é material de referência.
- O currículo curado (205 módulos) vive em `client/src/data/curriculum.json` e em
  `data/aprende.db`. `pnpm seed`/`build_curriculum.py` geram apenas um **esqueleto de teste**
  (10 módulos placeholder) — não usem para restaurar o currículo real.
- O JSON do navegador pode ser reexportado de `data/aprende.db` com
  `python -m scripts.export_curriculum`. CI executa `--check` para detectar dados desatualizados.

Os scripts usam **apenas a biblioteca padrão** do Python.

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

---

## Parte del indice educativo

Esta plataforma forma parte del conjunto educativo de **Belentani / NOIACORE**:
formacion gratuita y abierta. El mapa verificado del conjunto vive en este
repositorio: [`UNIVERSO-EDUCATIVO.md`](UNIVERSO-EDUCATIVO.md).

| Plataforma | Que ensena | Enlace |
|---|---|---|
| Open School | Instituto digital universal | [repositorio](https://github.com/belentani7/open-school) — sin despliegue |
| ManosAbiertas | IA y ofimatica para recien llegados | https://manos-abiertas-rho.vercel.app |
| WILLIAMSCHOOL | Plataforma ESO y tutoria cultural (PT→ES→CA) | https://williamschool-livid.vercel.app |
| UX Academy | Diseno UX/Producto, trilingue | https://ux-academy-professional.vercel.app |
| Aprende Brasil | Educacion para Brasil | https://aprende-brasil.vercel.app/ |
| Lingua Aberta | Idiomas, progresion CEFR | https://lingua-aberta.vercel.app/ |
| Cruzando el Charco | Acogida y arraigo | https://cruzando-el-charco-web-20260812.vercel.app |
| secure-t | Ciberseguridad e IA | [repositorio](https://github.com/belentani7/secure-t) — sin despliegue (repo archivado) |

**PT > ES > EN > CA.** Gratuito, accesible (WCAG) y conectado.
