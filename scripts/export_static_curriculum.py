#!/usr/bin/env python3
"""Exporta JSON estático de forma determinista desde SQLite de origem.

Não usa rede nem modifica SQLite; funciona em builds de Node/Vercel
com Python 3 standard library, sem instalar SQLAlchemy ou FastAPI.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATABASE = ROOT / "data" / "aprende.db"
OUTPUT = ROOT / "client" / "src" / "data" / "curriculum.json"


def export() -> dict:
    if not DATABASE.is_file():
        raise FileNotFoundError(f"Missing checked-in curriculum database: {DATABASE}")
    uri = f"file:{DATABASE.as_posix()}?mode=ro"
    with sqlite3.connect(uri, uri=True) as db:
        db.row_factory = sqlite3.Row
        tracks = []
        for t in db.execute("SELECT id,label,eyebrow,description,color,icon,target_modules FROM tracks ORDER BY id"):
            row = dict(t)
            row["module_count"] = db.execute(
                "SELECT COUNT(*) FROM modules WHERE track_id=?", (t["id"],)
            ).fetchone()[0]
            tracks.append(row)

        modules = []
        for m in db.execute("""
            SELECT id,track_id,title,subtitle,level,level_order,duration_min,age_group,
                   objectives,featured,accent,icon FROM modules ORDER BY level_order,title
        """):
            row = dict(m)
            row["featured"] = bool(row["featured"])
            row["steps"] = []
            for step in db.execute("""
                SELECT "order",step_type,title,content_json
                FROM module_steps WHERE module_id=? ORDER BY "order"
            """, (m["id"],)):
                row["steps"].append({
                    "order": step["order"],
                    "type": step["step_type"],
                    "title": step["title"],
                    "content": json.loads(step["content_json"]) if step["content_json"] else None,
                })
            modules.append(row)

    steps = sum(len(m["steps"]) for m in modules)
    if len(tracks) != 4 or len(modules) != 205 or steps != 1025:
        raise ValueError(f"Curriculum incomplete: {len(tracks)} tracks, {len(modules)} modules, {steps} steps")
    if any(not m["steps"] or any(not s["content"] for s in m["steps"]) for m in modules):
        raise ValueError("Empty curriculum step detected")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {"tracks": tracks, "modules": modules}
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return {"tracks": len(tracks), "modules": len(modules), "steps": steps, "output": str(OUTPUT.relative_to(ROOT)), "bytes": OUTPUT.stat().st_size}


if __name__ == "__main__":
    print(json.dumps(export(), ensure_ascii=False))
