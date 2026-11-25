"""Integridade do currículo publicado em data/aprende.db (205 módulos)."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

DB = Path(__file__).resolve().parents[1] / "data" / "aprende.db"
EXPECTED_TRACKS = {"alfabetizacao": 93, "informatica": 40, "matematica": 40, "idiomas": 32}
STEP_TYPES = ["explanation", "example", "practice", "check", "next"]


@pytest.fixture(scope="module")
def db():
    if not DB.exists():
        pytest.skip("data/aprende.db ausente — rode: pnpm seed")
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


def test_banco_existe(db):
    assert DB.stat().st_size > 0


def test_contagem_por_trilha(db):
    got = {r["track_id"]: r["n"] for r in db.execute(
        "select track_id, count(*) n from modules group by track_id")}
    assert got == EXPECTED_TRACKS


def test_total_modulos_e_etapas(db):
    assert db.execute("select count(*) from modules").fetchone()[0] == 205
    assert db.execute("select count(*) from module_steps").fetchone()[0] == 1025
    assert db.execute("select count(*) from tracks").fetchone()[0] == 4


def test_cada_modulo_tem_cinco_etapas_na_ordem(db):
    rows = db.execute(
        'select module_id, count(*) n, min("order") lo, max("order") hi '
        "from module_steps group by module_id"
    ).fetchall()
    assert len(rows) == 205
    for r in rows:
        assert r["n"] == 5, f"{r['module_id']} tem {r['n']} etapas"
        assert (r["lo"], r["hi"]) == (1, 5), f"{r['module_id']} fora de ordem"

    tipos = db.execute(
        "select distinct step_type from module_steps order by step_type").fetchall()
    assert sorted(t[0] for t in tipos) == sorted(STEP_TYPES)


def test_ids_unicos_e_titulos_preenchidos(db):
    total = db.execute("select count(*) from modules").fetchone()[0]
    distinct = db.execute("select count(distinct id) from modules").fetchone()[0]
    assert total == distinct
    vazios = db.execute(
        "select count(*) from modules where title is null or trim(title) = ''").fetchone()[0]
    assert vazios == 0


def test_content_json_sempre_valido(db):
    ruins = 0
    for (raw,) in db.execute("select content_json from module_steps"):
        try:
            if not isinstance(json.loads(raw), dict):
                ruins += 1
        except (TypeError, ValueError):
            ruins += 1
    assert ruins == 0


def test_toda_trilha_tem_modulos(db):
    orfas = db.execute(
        "select count(*) from modules m left join tracks t on t.id = m.track_id where t.id is null"
    ).fetchone()[0]
    assert orfas == 0
