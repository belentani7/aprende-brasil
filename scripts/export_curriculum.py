#!/usr/bin/env python3
"""Exporta o currículo SQLite usando apenas Python padrão.

Use ``--check`` em CI para detectar JSON desatualizado sem alterar arquivos.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "aprende.db"
OUT = ROOT / "client" / "src" / "data" / "curriculum.json"


def build_payload() -> dict:
    if not DB.is_file():
        raise FileNotFoundError(DB)
    db = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    try:
        counts = dict(db.execute("SELECT track_id, COUNT(*) FROM modules GROUP BY track_id"))
        tracks = [dict(row) | {"module_count": counts.get(row["id"], 0)}
                  for row in db.execute("SELECT id, label, eyebrow, description, color, icon, target_modules FROM tracks ORDER BY id")]
        steps_by_module: dict[str, list[dict]] = {}
        for row in db.execute('SELECT module_id, "order", step_type, title, content_json FROM module_steps ORDER BY module_id, "order"'):
            steps_by_module.setdefault(row["module_id"], []).append({
                "order": row["order"], "type": row["step_type"], "title": row["title"],
                "content": json.loads(row["content_json"]) if row["content_json"] else None,
            })
        modules = []
        for row in db.execute("""SELECT id, track_id, title, subtitle, level, level_order,
                              duration_min, age_group, objectives, featured, accent, icon
                              FROM modules ORDER BY level_order, title"""):
            modules.append({
                "id": row["id"], "track_id": row["track_id"], "title": row["title"],
                "subtitle": row["subtitle"], "level": row["level"],
                "level_order": row["level_order"], "duration_min": row["duration_min"],
                "age_group": row["age_group"], "objectives": row["objectives"],
                "featured": bool(row["featured"]), "accent": row["accent"],
                "icon": row["icon"], "steps": steps_by_module.get(row["id"], []),
            })
        return {"tracks": tracks, "modules": modules}
    finally:
        db.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="falha se o JSON versionado diferir do banco")
    args = parser.parse_args()
    payload = build_payload()
    rendered = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    if args.check:
        if not OUT.is_file() or OUT.read_text(encoding="utf-8") != rendered:
            parser.exit(1, f"Currículo ausente/desatualizado: {OUT}\nExecute python -m scripts.export_curriculum\n")
    else:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(rendered, encoding="utf-8")
    total_steps = sum(len(m["steps"]) for m in payload["modules"])
    print(f"{len(payload['modules'])} módulos, {total_steps} etapas -> {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
