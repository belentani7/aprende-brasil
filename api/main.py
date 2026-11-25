from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import Response
from starlette.types import Scope

from .database import engine, Base
from .routes import tracks, modules, tutor, progress

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Aprende Brasil API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tracks.router)
app.include_router(modules.router)
app.include_router(tutor.router)
app.include_router(progress.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "project": "aprende-brasil"}


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
