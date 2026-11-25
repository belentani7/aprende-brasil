"""O servidor de SPA não pode servir arquivos fora de dist/public."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from api.main import safe_static_path  # noqa: E402


@pytest.fixture()
def public(tmp_path: Path) -> Path:
    root = tmp_path / "dist" / "public"
    (root / "assets").mkdir(parents=True)
    (root / "index.html").write_text("<!doctype html>", encoding="utf-8")
    (root / "assets" / "app.js").write_text("console.log(1)", encoding="utf-8")
    (root / "404.html").write_text("nao encontrado", encoding="utf-8")
    (tmp_path / "segredo.txt").write_text("não deveria sair", encoding="utf-8")
    return root


def test_serve_arquivo_dentro_da_pasta(public):
    assert safe_static_path(public, "index.html") == public / "index.html"
    assert safe_static_path(public, "assets/app.js") == public / "assets" / "app.js"
    assert safe_static_path(public, "/assets/app.js") == public / "assets" / "app.js"


def test_bloqueia_traversal_com_pontos(public):
    assert safe_static_path(public, "../segredo.txt") is None
    assert safe_static_path(public, "../../etc/passwd") is None
    assert safe_static_path(public, "assets/../../segredo.txt") is None


def test_bloqueia_caminho_absoluto(public, tmp_path):
    assert safe_static_path(public, str(tmp_path / "segredo.txt")) is None


def test_bloqueia_symlink_que_aponta_para_fora(public, tmp_path):
    link = public / "atalho.txt"
    link.symlink_to(tmp_path / "segredo.txt")
    assert safe_static_path(public, "atalho.txt") is None


def test_arquivo_inexistente_e_nulo(public):
    assert safe_static_path(public, "nao-existe.js") is None
    assert safe_static_path(public, "") is None
