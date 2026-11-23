#!/usr/bin/env python3
"""Exporta o currículo do SQLite para JSON estático consumido pelo cliente.

Gera client/src/data/curriculum.json a partir de data/aprende.db, para que a
plataforma rode 100% no navegador (sem backend): Vercel, Netlify, Cloudflare
Pages ou GitHub Pages.

Rodar: python -m scripts.export_curriculum
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from api.database import SessionLocal  # noqa: E402
from api.models import Module, ModuleStep, Track  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "client" / "src" / "data" / "curriculum.json"


def main() -> int:
    db = SessionLocal()

    tracks = [
        {
            "id": t.id,
            "label": t.label,
            "eyebrow": t.eyebrow,
            "description": t.description,
            "color": t.color,
            "icon": t.icon,
            "target_modules": t.target_modules,
            "module_count": db.query(Module).filter(Module.track_id == t.id).count(),
        }
        for t in db.query(Track).order_by(Track.id).all()
    ]

    modules = []
    for m in db.query(Module).order_by(Module.level_order, Module.title).all():
        steps = (
            db.query(ModuleStep)
            .filter(ModuleStep.module_id == m.id)
            .order_by(ModuleStep.order)
            .all()
        )
        modules.append(
            {
                "id": m.id,
                "track_id": m.track_id,
                "title": m.title,
                "subtitle": m.subtitle,
                "level": m.level,
                "level_order": m.level_order,
                "duration_min": m.duration_min,
                "age_group": m.age_group,
                "objectives": m.objectives,
                "featured": bool(m.featured),
                "accent": m.accent,
                "icon": m.icon,
                "steps": [
                    {
                        "order": s.order,
                        "type": s.step_type,
                        "title": s.title,
                        "content": json.loads(s.content_json) if s.content_json else None,
                    }
                    for s in steps
                ],
            }
        )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {"tracks": tracks, "modules": modules}
    OUT.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    total_steps = sum(len(m["steps"]) for m in modules)
    print(
        f"{len(modules)} módulos, {total_steps} etapas -> "
        f"{OUT.relative_to(ROOT)} ({OUT.stat().st_size / 1024:.0f} KB)"
    )
    db.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
