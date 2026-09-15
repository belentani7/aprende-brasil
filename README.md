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
| API | FastAPI + SQLAlchemy (Python 3.11+) |
| Dados | SQLite (`data/aprende.db`) |
| Conteúdo | Scripts Python + banco de palavras aberto |

```
client/    frontend React
api/       backend FastAPI (main, models, routes/)
scripts/   fetch_open_data.py, build_curriculum.py
data/      aprende.db + open/palavras-pt.txt
dist/public  build do frontend (vite build)
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

## API

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

## Bancos de dados abertos

- **Lista de palavras do português** — [pythonprobr/palavras](https://github.com/pythonprobr/palavras) (MIT),
  baixada e normalizada por `scripts/fetch_open_data.py` em `data/open/palavras-pt.txt`.
- O currículo é construído por `scripts/build_curriculum.py` a partir dessa base
  e de listas curadas (informática, matemática, idiomas).

Os scripts usam **apenas a biblioteca padrão** para o download.

## Tutor Nilo (LLM opcional)

Sem configuração, o tutor responde com orientações locais (offline). Para usar um
LLM, defina variáveis de ambiente (endpoint OpenAI-compatível):

```
LLM_API_URL=https://api.exemplo.com/v1/chat/completions
LLM_API_KEY=...
LLM_MODEL=gpt-4o-mini
```

## Deploy

- **Frontend** (`dist/public`): estático, vai para Vercel / Cloudflare Pages
  (`vercel.json` já configurado com `vite build`).
- **Backend** (FastAPI): precisa de host Python (Render, Fly.io, Railway ou VPS).
  Um host estático não executa o backend — para produção completa, sirva o SPA
  pelo próprio FastAPI (`pnpm start`) ou aponte `VITE_API_URL` para o backend.

## Próximos passos

- Mais temas de alfabetização (transporte, saúde, trabalho) e exercícios com correção.
- Importador de módulos versionado + revisão editorial.
- Perfis de docente/editor, metas e agenda persistidas.
- Voz (OpenVoice/TTS) atrás de um adaptador server-side.
- Revisão WCAG 2.2 AA com usuários reais.

## Licença

MIT.
