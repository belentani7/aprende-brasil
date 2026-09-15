"""Fixtures compartilhadas dos testes da Aprende Brasil."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from api.database import Base, get_db  # noqa: E402
from api.models import Module, ModuleStep, Track  # noqa: E402

STEP_TYPES = ["explanation", "example", "practice", "check", "next"]


def _seed(db):
    db.add(Track(id="alfabetizacao", label="Alfabetização", eyebrow="Ler e escrever",
                 description="Primeiros passos", color="orange", icon="BookOpen", target_modules=0))
    db.add(Track(id="matematica", label="Matemática", eyebrow="Raciocínio aplicado",
                 description="Números", color="violet", icon="BarChart3", target_modules=0))

    db.add(Module(id="alfa-letra-a", track_id="alfabetizacao", title="A letra A",
                  subtitle="Vogal A", level="Começo", level_order=0, duration_min=8,
                  featured=True, accent="orange", icon="BookOpen"))
    db.flush()
    for i, tp in enumerate(STEP_TYPES, 1):
        db.add(ModuleStep(module_id="alfa-letra-a", order=i, step_type=tp,
                          title=f"Etapa {i}", content_json=json.dumps({"text": f"texto {i}"}, ensure_ascii=False)))

    db.add(Module(id="mat-soma", track_id="matematica", title="Somar com as mãos",
                  subtitle="2 + 3", level="Essencial", level_order=0, duration_min=12,
                  featured=False, accent="violet", icon="BarChart3"))
    db.commit()


@pytest.fixture()
def client(tmp_path):
    """TestClient com um SQLite isolado por teste (não toca data/aprende.db)."""
    engine = create_engine(f"sqlite:///{tmp_path / 'test.db'}")
    TestingSession = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSession()
    _seed(db)
    db.close()

    def override_get_db():
        session = TestingSession()
        try:
            yield session
        finally:
            session.close()

    from api.main import app

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as c:
            yield c
    finally:
        app.dependency_overrides.clear()


@pytest.fixture()
def no_llm(monkeypatch):
    """Garante que o tutor use o fallback local, sem chamadas de rede."""
    for var in ("LLM_API_URL", "LLM_API_KEY", "LLM_MODEL"):
        monkeypatch.delenv(var, raising=False)
