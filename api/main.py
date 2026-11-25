"""Aplicação FastAPI da Aprende Brasil.

Dois modos convivem:

- **Estático** (padrão e recomendado): o site é um build estático, o progresso
  fica no navegador e o backend nem precisa existir.
- **Com sessão**: quando este servidor está no ar, o progresso pode ser
  sincronizado por uma sessão anônima. Todas as rotas de dados exigem o
  cabeçalho ``Authorization: Bearer <token>``; nenhuma aceita ``user_id``.

Configuração por ambiente (nunca por código versionado):

- ``APRENDE_CORS_ORIGINS`` — lista separada por vírgula. Vazio = sem CORS
  (o padrão, já que o site estático não faz chamadas cross-origin).
- ``APRENDE_DB`` — caminho alternativo do SQLite.
"""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import Response
from starlette.types import Scope

from .database import engine, Base
from .routes import tracks, modules, tutor, progress, session as session_routes

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Aprende Brasil API",
    version="1.2.0",
    description=(
        "Conteúdo curricular e sessões anônimas. O campus estático não depende "
        "deste servidor para funcionar."
    ),
)

_cors_origins = [
    origin.strip()
    for origin in os.environ.get("APRENDE_CORS_ORIGINS", "").split(",")
    if origin.strip()
]
if _cors_origins:
    # Lista explícita, sem curinga: credenciais de sessão nunca viajam para
    # qualquer origem.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_cors_origins,
        allow_methods=["GET", "POST", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
        max_age=600,
    )

app.include_router(tracks.router)
app.include_router(modules.router)
app.include_router(tutor.router)
app.include_router(session_routes.router)
app.include_router(progress.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "project": "aprende-brasil", "version": "1.2.0"}


# Serve React frontend in production (Vite output: dist/public)
CLIENT_DIST = Path(__file__).resolve().parent.parent / "dist" / "public"


class SPAStaticFiles(StaticFiles):
    """Arquivos estáticos com fallback para o index.html das rotas do SPA.

    ``StaticFiles`` resolve o caminho com segurança (não sai do diretório e
    bloqueia symlinks), mas devolve 404 em ``/modulo/alfa-letra-a``. Aqui uma
    rota sem extensão que não existe vira ``index.html`` e o React Router
    decide a tela; um arquivo com extensão ausente continua 404 (um ``.js``
    faltando não pode virar HTML).
    """

    async def get_response(self, path: str, scope: Scope) -> Response:
        try:
            response = await super().get_response(path, scope)
        except StarletteHTTPException as exc:
            if exc.status_code != 404 or "." in Path(path).name:
                raise
            return await super().get_response("index.html", scope)
        if response.status_code == 404 and "." not in Path(path).name:
            return await super().get_response("index.html", scope)
        return response


if CLIENT_DIST.is_dir():
    app.mount(
        "/",
        SPAStaticFiles(directory=CLIENT_DIST, html=True),
        name="spa",
    )
