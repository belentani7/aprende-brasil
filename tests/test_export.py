"""O JSON estático exportado deve espelhar exatamente o SQLite."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "aprende.db"
JSON = ROOT / "client" / "src" / "data" / "curriculum.json"
EXPECTED_TRACKS = {"alfabetizacao": 93, "informatica": 40, "matematica": 40, "idiomas": 32}


@pytest.fixture(scope="module")
def payload():
    if not JSON.exists():
        pytest.skip("curriculum.json ausente — rode: python -m scripts.export_curriculum")
    return json.loads(JSON.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def db():
    if not DB.exists():
        pytest.skip("data/aprende.db ausente — rode: pnpm seed")
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


def test_estrutura_do_json(payload):
    assert set(payload) == {"tracks", "modules"}
    assert len(payload["tracks"]) == 4
    assert len(payload["modules"]) == 205


def test_modulos_batem_com_o_banco(payload, db):
    ids_json = {m["id"] for m in payload["modules"]}
    ids_db = {r["id"] for r in db.execute("select id from modules")}
    assert ids_json == ids_db


def test_contagem_por_trilha(payload):
    got: dict[str, int] = {}
    for m in payload["modules"]:
        got[m["track_id"]] = got.get(m["track_id"], 0) + 1
    assert got == EXPECTED_TRACKS


def test_module_count_das_trilhas_confere(payload):
    for t in payload["tracks"]:
        assert t["module_count"] == EXPECTED_TRACKS[t["id"]]


def test_cada_modulo_tem_cinco_etapas_ordenadas(payload):
    total = 0
    for m in payload["modules"]:
        steps = m["steps"]
        total += len(steps)
        assert [s["order"] for s in steps] == [1, 2, 3, 4, 5], m["id"]
        for s in steps:
            assert isinstance(s["content"], dict)
            assert s["content"].get("text")
    assert total == 1025


def test_textos_batem_com_o_banco(payload, db):
    """A primeira etapa exportada deve ser idêntica à do SQLite."""
    by_id = {m["id"]: m for m in payload["modules"]}
    for row in db.execute(
        'select module_id, "order" as ord, content_json from module_steps where "order" = 1'
    ):
        exported = by_id[row["module_id"]]["steps"][0]["content"]
        assert exported == json.loads(row["content_json"]), row["module_id"]
