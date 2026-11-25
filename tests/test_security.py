"""O servidor de SPA entrega só o que está em dist/public e faz fallback do SPA."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from api.main import SPAStaticFiles  # noqa: E402


@pytest.fixture()
def client(tmp_path: Path) -> TestClient:
    public = tmp_path / "dist" / "public"
    (public / "assets").mkdir(parents=True)
    (public / "index.html").write_text("<!doctype html><title>SPA</title>", encoding="utf-8")
    (public / "assets" / "app.js").write_text("console.log(1)", encoding="utf-8")
    (public / "favicon.svg").write_text("<svg/>", encoding="utf-8")
    (tmp_path / "segredo.txt").write_text("não deveria sair", encoding="utf-8")

    app = FastAPI()
    app.mount("/", SPAStaticFiles(directory=public, html=True), name="spa")
    return TestClient(app)


def test_serve_arquivos_publicos(client):
    assert client.get("/").text == "<!doctype html><title>SPA</title>"
    assert client.get("/assets/app.js").text == "console.log(1)"
    assert client.get("/favicon.svg").text == "<svg/>"


def test_rota_do_spa_recebe_index(client):
    for route in ("/modulo/alfa-letra-a", "/sobre", "/nao-existe"):
        response = client.get(route)
        assert response.status_code == 200
        assert "<title>SPA</title>" in response.text


def test_arquivo_com_extensao_ausente_continua_404(client):
    response = client.get("/assets/nao-existe.js")
    assert response.status_code == 404
    assert "não deveria sair" not in response.text


def test_bloqueia_traversal(client):
    for attempt in ("/../segredo.txt", "/%2e%2e/segredo.txt", "/assets/../../segredo.txt"):
        response = client.get(attempt)
        assert "não deveria sair" not in response.text


def test_symlink_para_fora_nao_e_servido(client, tmp_path):
    public = tmp_path / "dist" / "public"
    (public / "atalho.txt").symlink_to(tmp_path / "segredo.txt")
    response = client.get("/atalho.txt")
    assert "não deveria sair" not in response.text
