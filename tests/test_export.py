"""Os JSON estáticos exportados devem espelhar exatamente o SQLite."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "aprende.db"
CATALOG = ROOT / "client" / "src" / "data" / "curriculum.json"
STEPS = ROOT / "client" / "src" / "data" / "curriculum-steps.json"
EXPECTED_TRACKS = {"alfabetizacao": 93, "informatica": 40, "matematica": 40, "idiomas": 32}
STEP_TYPES = ["explanation", "example", "practice", "check", "next"]


@pytest.fixture(scope="module")
def catalog():
    if not CATALOG.exists():
        pytest.skip("curriculum.json ausente — rode: python3 scripts/export_static_curriculum.py")
    return json.loads(CATALOG.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def steps():
    if not STEPS.exists():
        pytest.skip("curriculum-steps.json ausente — rode: python3 scripts/export_static_curriculum.py")
    return json.loads(STEPS.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def db():
    if not DB.exists():
        pytest.skip("data/aprende.db ausente — rode: python3 -m scripts.build_curriculum")
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


def test_estrutura_do_catalogo(catalog):
    assert set(catalog) == {"tracks", "modules"}
    assert len(catalog["tracks"]) == 4
    assert len(catalog["modules"]) == 205


def test_modulos_batem_com_o_banco(catalog, db):
    ids_json = {m["id"] for m in catalog["modules"]}
    ids_db = {r["id"] for r in db.execute("select id from modules")}
    assert ids_json == ids_db


def test_contagem_por_trilha(catalog):
    got: dict[str, int] = {}
    for m in catalog["modules"]:
        got[m["track_id"]] = got.get(m["track_id"], 0) + 1
    assert got == EXPECTED_TRACKS


def test_module_count_das_trilhas_confere(catalog):
    for t in catalog["tracks"]:
        assert t["module_count"] == EXPECTED_TRACKS[t["id"]]


def test_catalogo_nao_carrega_as_etapas(catalog):
    """O catálogo é o payload leve da tela inicial: sem textos de etapa."""
    for m in catalog["modules"]:
        assert "steps" not in m
        assert m["step_count"] == 5


def test_etapas_exportadas_em_ordem_e_com_texto(steps, catalog):
    assert set(steps) == {m["id"] for m in catalog["modules"]}
    total = 0
    for module_id, module_steps in steps.items():
        total += len(module_steps)
        assert [s["order"] for s in module_steps] == [1, 2, 3, 4, 5], module_id
        assert [s["type"] for s in module_steps] == STEP_TYPES, module_id
        for step in module_steps:
            assert isinstance(step["content"], dict), module_id
            assert step["content"].get("text", "").strip(), module_id
    assert total == 1025


def test_textos_batem_com_o_banco(steps, db):
    """Cada etapa exportada deve ser idêntica à registrada no SQLite."""
    for row in db.execute('select module_id, "order" as ord, title, step_type, content_json from module_steps'):
        exported = steps[row["module_id"]][row["ord"] - 1]
        assert exported["title"] == row["title"]
        assert exported["type"] == row["step_type"]
        assert exported["content"] == json.loads(row["content_json"]), row["module_id"]
