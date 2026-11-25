#!/usr/bin/env python3
"""Exporta o currículo estático em dois arquivos, de forma determinista.

Por que dois arquivos: o catálogo (tracks + metadados dos módulos) é pequeno e
carrega junto com a tela inicial; as 1.025 etapas somam a maior parte dos bytes
e só são necessárias ao abrir um módulo ou ao usar o tutor. Separando os dados,
o JavaScript inicial fica bem menor e o conteúdo completo vira um chunk sob
demanda.

Saídas (ambas geradas, nunca editadas à mão):
  client/src/data/curriculum.json        -> {"tracks": [...], "modules": [...]}
  client/src/data/curriculum-steps.json  -> {"<id-do-módulo>": [etapas...]}

Não usa rede nem modifica o SQLite: apenas sqlite3 da biblioteca padrão, o que
permite rodar no build da Vercel sem instalar SQLAlchemy.
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATABASE = ROOT / "data" / "aprende.db"
DATA_DIR = ROOT / "client" / "src" / "data"
CATALOG = DATA_DIR / "curriculum.json"
STEPS = DATA_DIR / "curriculum-steps.json"

EXPECTED_TRACKS = 4
EXPECTED_MODULES = 205
EXPECTED_STEPS = 1025
STEP_TYPES = ["explanation", "example", "practice", "check", "next"]


def _serialize(payload: object) -> str:
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def _write(path: Path, payload: object) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_serialize(payload), encoding="utf-8")
    return path.stat().st_size


def export(check: bool = False) -> dict:
    if not DATABASE.is_file():
        raise FileNotFoundError(f"Banco do currículo ausente: {DATABASE}")

    uri = f"file:{DATABASE.as_posix()}?mode=ro"
    with sqlite3.connect(uri, uri=True) as db:
        db.row_factory = sqlite3.Row
        tracks = []
        for t in db.execute(
            "SELECT id,label,eyebrow,description,color,icon,target_modules "
            "FROM tracks ORDER BY id"
        ):
            row = dict(t)
            row["module_count"] = db.execute(
                "SELECT COUNT(*) FROM modules WHERE track_id=?", (t["id"],)
            ).fetchone()[0]
            tracks.append(row)

        modules = []
        for m in db.execute(
            """
            SELECT id,track_id,title,subtitle,level,level_order,duration_min,
                   age_group,objectives,featured,accent,icon
            FROM modules ORDER BY level_order,title
            """
        ):
            row = dict(m)
            row["featured"] = bool(row["featured"])
            row["step_count"] = db.execute(
                "SELECT COUNT(*) FROM module_steps WHERE module_id=?", (m["id"],)
            ).fetchone()[0]
            modules.append(row)

        steps_by_module: dict[str, list[dict]] = {}
        for s in db.execute(
            'SELECT module_id,"order",step_type,title,content_json '
            'FROM module_steps ORDER BY module_id,"order"'
        ):
            content = json.loads(s["content_json"]) if s["content_json"] else None
            steps_by_module.setdefault(s["module_id"], []).append(
                {
                    "order": s["order"],
                    "type": s["step_type"],
                    "title": s["title"],
                    "content": content,
                }
            )

    # ── Validação: falhar no build é melhor que publicar currículo quebrado ──
    total_steps = sum(len(v) for v in steps_by_module.values())
    if len(tracks) != EXPECTED_TRACKS or len(modules) != EXPECTED_MODULES:
        raise ValueError(
            f"Currículo incompleto: {len(tracks)} trilhas, {len(modules)} módulos"
        )
    if total_steps != EXPECTED_STEPS:
        raise ValueError(f"Currículo incompleto: {total_steps} etapas")

    module_ids = {m["id"] for m in modules}
    if set(steps_by_module) != module_ids:
        raise ValueError("Há módulo sem etapas ou etapa de módulo inexistente")

    for module in modules:
        steps = steps_by_module[module["id"]]
        if [s["order"] for s in steps] != [1, 2, 3, 4, 5]:
            raise ValueError(f"{module['id']}: etapas fora da ordem 1..5")
        if [s["type"] for s in steps] != STEP_TYPES:
            raise ValueError(f"{module['id']}: tipos de etapa fora do padrão")
        for step in steps:
            content = step["content"]
            if not isinstance(content, dict) or not str(content.get("text", "")).strip():
                raise ValueError(f"{module['id']}/{step['order']}: etapa sem texto")

    catalog_payload = {"tracks": tracks, "modules": modules}
    if check:
        for path, payload in ((CATALOG, catalog_payload), (STEPS, steps_by_module)):
            if not path.is_file():
                raise SystemExit(f"Arquivo gerado ausente: {path.relative_to(ROOT)}")
            if path.read_text(encoding="utf-8") != _serialize(payload):
                raise SystemExit(
                    f"{path.relative_to(ROOT)} está desatualizado. "
                    "Rode: python3 scripts/export_static_curriculum.py"
                )
        catalog_bytes = CATALOG.stat().st_size
        steps_bytes = STEPS.stat().st_size
    else:
        catalog_bytes = _write(CATALOG, catalog_payload)
        steps_bytes = _write(STEPS, steps_by_module)

    return {
        "tracks": len(tracks),
        "modules": len(modules),
        "steps": total_steps,
        "catalog_bytes": catalog_bytes,
        "steps_bytes": steps_bytes,
        "catalog": str(CATALOG.relative_to(ROOT)),
        "steps_file": str(STEPS.relative_to(ROOT)),
    }


if __name__ == "__main__":
    print(json.dumps(export(check="--check" in sys.argv), ensure_ascii=False))
