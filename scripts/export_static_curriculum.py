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
ACTIVITY_KINDS = {
    "multiple-choice",
    "true-false",
    "fill-blank",
    "ordering",
    "matching",
    "numeric",
}
MIN_ACTIVITIES = 400


def _serialize(payload: object) -> str:
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def validate_step_content(module_id: str, step: dict) -> None:
    """Valida o contrato StepData (texto + campos novos) direto no exportador.

    O exportador roda só com a stdlib no build (sem importar FastAPI), então as
    regras essenciais das atividades são reaplicadas aqui: se o SQLite tiver
    atividade quebrada, o JSON não é gerado.
    """
    content = step["content"]
    path = f"{module_id}/{step['order']}"
    activities = content.get("activities")
    if activities is None:
        return
    if not isinstance(activities, list) or len(activities) > 4:
        raise ValueError(f"{path}: lista de atividades inválida")
    seen_ids: set[str] = set()
    for activity in activities:
        kind = activity.get("kind")
        if kind not in ACTIVITY_KINDS:
            raise ValueError(f"{path}: atividade com kind inválido {kind!r}")
        activity_id = activity.get("id")
        if not activity_id or activity_id in seen_ids:
            raise ValueError(f"{path}: atividade sem id ou id repetido {activity_id!r}")
        seen_ids.add(activity_id)
        if kind == "multiple-choice":
            options = activity.get("options") or []
            index = activity.get("correctIndex")
            if not isinstance(index, int) or not (0 <= index < len(options)):
                raise ValueError(f"{path}/{activity_id}: correctIndex fora das opções")
            if len(set(options)) != len(options):
                raise ValueError(f"{path}/{activity_id}: opções repetidas")
        elif kind == "true-false":
            if not isinstance(activity.get("answer"), bool):
                raise ValueError(f"{path}/{activity_id}: answer não é booleano")
        elif kind == "fill-blank":
            if not activity.get("acceptedAnswers"):
                raise ValueError(f"{path}/{activity_id}: sem respostas aceitas")
        elif kind == "ordering":
            items = activity.get("items") or []
            order = activity.get("correctOrder") or []
            if sorted(order) != list(range(len(items))):
                raise ValueError(f"{path}/{activity_id}: correctOrder inválida")
        elif kind == "matching":
            pairs = activity.get("pairs") or []
            if len(pairs) < 2:
                raise ValueError(f"{path}/{activity_id}: pares insuficientes")
        elif kind == "numeric":
            if not isinstance(activity.get("answer"), (int, float)):
                raise ValueError(f"{path}/{activity_id}: resposta não numérica")
            if float(activity.get("tolerance", -1)) < 0:
                raise ValueError(f"{path}/{activity_id}: tolerância negativa")


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
            validate_step_content(module["id"], step)

    activities = sum(
        len(step["content"].get("activities") or [])
        for steps_list in steps_by_module.values()
        for step in steps_list
    )
    if activities < MIN_ACTIVITIES:
        raise ValueError(
            f"Atividades insuficientes no currículo: {activities} (mínimo {MIN_ACTIVITIES})"
        )

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
        "activities": activities,
        "catalog_bytes": catalog_bytes,
        "steps_bytes": steps_bytes,
        "catalog": str(CATALOG.relative_to(ROOT)),
        "steps_file": str(STEPS.relative_to(ROOT)),
    }


if __name__ == "__main__":
    print(json.dumps(export(check="--check" in sys.argv), ensure_ascii=False))
