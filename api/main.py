from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

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
CLIENT_DIST = os.path.join(os.path.dirname(__file__), "..", "dist", "public")
if os.path.isdir(CLIENT_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(CLIENT_DIST, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = os.path.join(CLIENT_DIST, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(CLIENT_DIST, "index.html"))
