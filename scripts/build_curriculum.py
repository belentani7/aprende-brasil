#!/usr/bin/env python3
"""Gera o currículo da Aprende Brasil (205 módulos) e popula o SQLite.

- Alfabetização / Informática / Matemática / Idiomas: conteúdo pedagógico real,
  curado em scripts/content_*.py (5 etapas por módulo, sem placeholders).

Rodar: python -m scripts.build_curriculum
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from api.database import Base, SessionLocal, engine  # noqa: E402
from api.models import Module, ModuleStep, Track  # noqa: E402
from scripts.content_alfabetizacao import ALFABETIZACAO  # noqa: E402
from scripts.content_idiomas import IDIOMAS  # noqa: E402
from scripts.content_informatica import INFORMATICA  # noqa: E402
from scripts.content_matematica import MATEMATICA  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

TRACKS = {
    "alfabetizacao": ("Alfabetização", "Ler e escrever", "Primeiros passos na leitura e escrita em português brasileiro.", "orange", "BookOpen"),
    "informatica": ("Informática", "Pensamento digital", "Do primeiro clique à criação de projetos digitais.", "blue", "Code2"),
    "matematica": ("Matemática", "Raciocínio aplicado", "Números, formas e decisões para a vida real.", "violet", "BarChart3"),
    "idiomas": ("Idiomas", "Comunicação global", "Pratique inglês, espanhol e português no seu ritmo.", "green", "Languages"),
}


def steps(*rows) -> list[tuple[str, str, str]]:
    """Cada row: (tipo, título, texto)."""
    return list(rows)


def add(db, mid, track, title, subtitle, level, order, duration, featured, step_rows):
    if db.get(Module, mid):
        return
    label, eyebrow, desc, color, icon = TRACKS[track]
    db.add(Module(
        id=mid, track_id=track, title=title, subtitle=subtitle, level=level,
        level_order=order, duration_min=duration, featured=featured, accent=color, icon=icon,
    ))
    db.flush()
    for i, (tp, tt, tx) in enumerate(step_rows, 1):
        db.add(ModuleStep(module_id=mid, order=i, step_type=tp, title=tt,
                          content_json=json.dumps({"text": tx}, ensure_ascii=False)))


# ── Alfabetização ────────────────────────────────────────────────────────
def seed_alfabetizacao(db):
    """Semeia os 93 módulos curados de alfabetização (scripts/content_alfabetizacao.py)."""
    for mid, title, subtitle, level, order, duration, featured, step_rows in ALFABETIZACAO:
        add(db, mid, "alfabetizacao", title, subtitle, level, order, duration, featured, step_rows)
    return len(ALFABETIZACAO)


# ── Informática / Matemática / Idiomas ───────────────────────────────────
def seed_from_content(db, track: str, level: str, items) -> int:
    """Semeia módulos com conteúdo curado: (id, título, subtítulo, etapas)."""
    for i, (mid, title, sub, step_rows) in enumerate(items):
        add(db, mid, track, title, sub, level, i // 8, 12 + (i % 3) * 2, i % 7 == 0, step_rows)
    return len(items)


def main() -> int:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    # Rebuild determinístico do catálogo
    db.query(ModuleStep).delete()
    db.query(Module).delete()
    db.query(Track).delete()
    db.commit()
    for tid, (label, eyebrow, desc, color, icon) in TRACKS.items():
        db.add(Track(id=tid, label=label, eyebrow=eyebrow, description=desc, color=color, icon=icon, target_modules=0))
    db.commit()

    n = 0
    n += seed_alfabetizacao(db)
    n += seed_from_content(db, "informatica", "Começo", INFORMATICA)
    n += seed_from_content(db, "matematica", "Essencial", MATEMATICA)
    n += seed_from_content(db, "idiomas", "A1 · Iniciante", IDIOMAS)
    db.commit()

    for tid in TRACKS:
        c = db.query(Module).filter(Module.track_id == tid).count()
        print(f"  {TRACKS[tid][0]}: {c} módulos")
    total = db.query(Module).count()
    print(f"\nTotal: {total} módulos, {db.query(ModuleStep).count()} etapas")
    db.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
