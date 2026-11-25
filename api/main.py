from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

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


def safe_static_path(root: Path, requested: str) -> Path | None:
    """Resolve um arquivo pedido pelo cliente sem sair da pasta pública.

    O caminho da URL é dado por quem chama o servidor; concatenar direto abriria
    leitura arbitrária (``/../api/main.py``, ``/../../etc/passwd``). Aqui o
    caminho é resolvido e só é aceito se continuar dentro de ``root``.
    """
    try:
        candidate = (root / requested.lstrip("/")).resolve()
    except (OSError, ValueError):
        return None
    if not candidate.is_relative_to(root.resolve()):
        return None
    return candidate if candidate.is_file() else None


if CLIENT_DIST.is_dir():
    assets = CLIENT_DIST / "assets"
    if assets.is_dir():
        app.mount("/assets", StaticFiles(directory=assets), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        static_file = safe_static_path(CLIENT_DIST, full_path)
        if static_file is not None:
            return FileResponse(static_file)
        index = CLIENT_DIST / "index.html"
        if not index.is_file():
            raise HTTPException(status_code=404, detail="Frontend não compilado")
        return FileResponse(index)
