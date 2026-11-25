"""Privacidade: identidade vem da sessão, nunca do cliente.

Estes testes existem porque a versão anterior aceitava ``user_id`` no corpo e na
query string e caía em ``DEFAULT_USER = 1``. Exposto publicamente, isso permitia
ler e alterar o progresso de qualquer identificador.
"""

from __future__ import annotations

import json

import pytest


def start(client) -> tuple[str, dict]:
    r = client.post("/api/session")
    assert r.status_code == 200
    body = r.json()
    return body["token"], {"Authorization": f"Bearer {body['token']}"}


# ── Sem sessão, nenhum dado ─────────────────────────────────────────────


@pytest.mark.parametrize(
    "method,path",
    [
        ("get", "/api/progress"),
        ("get", "/api/stats"),
        ("get", "/api/favorites"),
        ("get", "/api/export"),
    ],
)
def test_rotas_de_dados_exigem_sessao(client, method, path):
    r = getattr(client, method)(path)
    assert r.status_code == 401
    assert r.json()["detail"] == "Autenticação necessária"


def test_escrita_exige_sessao(client):
    r = client.post("/api/progress", json={"module_id": "alfa-letra-a", "percent": 50})
    assert r.status_code == 401
    r = client.post("/api/favorites", json={"module_id": "mat-soma"})
    assert r.status_code == 401
    assert client.delete("/api/progress").status_code == 401


def test_token_invalido_nao_vira_sessao(client):
    r = client.get("/api/progress", headers={"Authorization": "Bearer nao-existe"})
    assert r.status_code == 401
    assert r.json()["detail"] == "Sessão inválida"


def test_token_em_texto_puro_nao_e_aceito(client):
    token, headers = start(client)
    r = client.get("/api/progress", headers={"Authorization": token})
    assert r.status_code == 401


# ── Isolamento entre estudantes ─────────────────────────────────────────


def test_progresso_de_um_estudante_nao_vaza_para_outro(client):
    _, alice = start(client)
    _, bruno = start(client)

    client.post(
        "/api/progress",
        json={"module_id": "alfa-letra-a", "percent": 80},
        headers=alice,
    )

    assert client.get("/api/progress", headers=alice).json()[0]["percent"] == 80
    assert client.get("/api/progress", headers=bruno).json() == []
    assert client.get("/api/stats", headers=bruno).json()["started"] == 0


def test_favoritos_sao_por_sessao(client):
    _, alice = start(client)
    _, bruno = start(client)

    client.post("/api/favorites", json={"module_id": "mat-soma"}, headers=alice)
    assert client.get("/api/favorites", headers=alice).json() == ["mat-soma"]
    assert client.get("/api/favorites", headers=bruno).json() == []


def test_user_id_no_corpo_e_rejeitado(client):
    """Nenhum endpoint aceita identidade do cliente (``extra="forbid"``)."""
    _, headers = start(client)
    r = client.post(
        "/api/progress",
        json={"user_id": 1, "module_id": "alfa-letra-a", "percent": 10},
        headers=headers,
    )
    assert r.status_code == 422
    r = client.post(
        "/api/favorites", json={"user_id": 1, "module_id": "mat-soma"}, headers=headers
    )
    assert r.status_code == 422


def test_user_id_na_query_string_e_ignorado(client):
    _, alice = start(client)
    _, bruno = start(client)
    client.post(
        "/api/progress",
        json={"module_id": "alfa-letra-a", "percent": 100},
        headers=alice,
    )
    # Tentativa de ler o progresso de outra pessoa via query string.
    r = client.get("/api/progress?user_id=1", headers=bruno)
    assert r.status_code == 200
    assert r.json() == []
    assert client.get("/api/stats?user_id=1", headers=bruno).json()["started"] == 0


def test_tokens_sao_unicos_e_nao_ficam_em_texto_no_banco(client, tmp_path):
    token_a, _ = start(client)
    token_b, _ = start(client)
    assert token_a != token_b

    from api.auth import hash_token

    # O banco de teste fica em tmp_path dentro do fixture; buscamos pela sessão
    # criada e conferimos que só o hash (64 hex) foi persistido.
    from api.main import app

    override = app.dependency_overrides[__import__("api.database", fromlist=["get_db"]).get_db]
    gen = override()
    db = next(gen)
    try:
        from api.models import UserSession

        stored = [row.token_hash for row in db.query(UserSession).all()]
        assert token_a not in stored
        assert hash_token(token_a) in stored
        assert all(len(h) == 64 for h in stored)
    finally:
        gen.close()


# ── Escritas idempotentes e monotônicas ─────────────────────────────────


def test_progresso_nao_regride_e_e_idempotente(client):
    _, headers = start(client)
    body = {"module_id": "alfa-letra-a", "percent": 60}
    for _ in range(3):
        r = client.post("/api/progress", json=body, headers=headers)
        assert r.status_code == 200
        assert r.json()["percent"] == 60

    r = client.post(
        "/api/progress",
        json={"module_id": "alfa-letra-a", "percent": 20},
        headers=headers,
    )
    assert r.json()["percent"] == 60
    rows = client.get("/api/progress", headers=headers).json()
    assert len(rows) == 1


def test_etapas_concluidas_se_acumulam_e_sao_validadas(client):
    _, headers = start(client)
    client.post(
        "/api/progress",
        json={"module_id": "alfa-letra-a", "percent": 20, "completed": [1, 2]},
        headers=headers,
    )
    r = client.post(
        "/api/progress",
        json={
            "module_id": "alfa-letra-a",
            "percent": 40,
            "completed": [2, 3, 99, 0, -1],
        },
        headers=headers,
    )
    assert r.json()["completed"] == [1, 2, 3]


def test_modulo_inexistente_404_com_sessao(client):
    _, headers = start(client)
    r = client.post(
        "/api/progress",
        json={"module_id": "nao-existe", "percent": 10},
        headers=headers,
    )
    assert r.status_code == 404


def test_percentual_invalido_422(client):
    _, headers = start(client)
    r = client.post(
        "/api/progress",
        json={"module_id": "alfa-letra-a", "percent": 150},
        headers=headers,
    )
    assert r.status_code == 422


def test_favorito_toggle_idempotente_sob_duplo_clique(client):
    _, headers = start(client)
    first = client.post("/api/favorites", json={"module_id": "mat-soma"}, headers=headers)
    assert first.json() == {"favorited": True, "module_id": "mat-soma"}
    second = client.post("/api/favorites", json={"module_id": "mat-soma"}, headers=headers)
    assert second.json() == {"favorited": False, "module_id": "mat-soma"}
    assert client.get("/api/favorites", headers=headers).json() == []


# ── Portabilidade ───────────────────────────────────────────────────────


def test_export_e_import_do_proprio_estudante(client):
    _, headers = start(client)
    client.post(
        "/api/progress",
        json={"module_id": "alfa-letra-a", "percent": 100, "completed": [1, 2, 3, 4, 5]},
        headers=headers,
    )
    client.post("/api/favorites", json={"module_id": "mat-soma"}, headers=headers)

    exported = client.get("/api/export", headers=headers).json()
    assert exported["version"] == 1
    assert exported["progress"] == {"alfa-letra-a": 100}
    assert exported["favorites"] == ["mat-soma"]
    assert exported["completed"] == {"alfa-letra-a": [1, 2, 3, 4, 5]}

    _, outro = start(client)
    r = client.post("/api/import", json=exported, headers=outro)
    assert r.status_code == 200
    assert r.json()["imported_modules"] == 1
    assert client.get("/api/stats", headers=outro).json()["completed"] == 1


def test_import_ignora_modulos_desconhecidos(client):
    _, headers = start(client)
    payload = {
        "version": 1,
        "progress": {"nao-existe": 100, "mat-soma": 50},
        "completed": {},
        "favorites": ["nao-existe"],
    }
    r = client.post("/api/import", json=payload, headers=headers)
    assert r.status_code == 200
    assert r.json()["imported_modules"] == 1
    assert client.get("/api/favorites", headers=headers).json() == []


def test_import_nao_reduz_progresso_existente(client):
    _, headers = start(client)
    client.post(
        "/api/progress",
        json={"module_id": "mat-soma", "percent": 90},
        headers=headers,
    )
    payload = {"version": 1, "progress": {"mat-soma": 10}}
    client.post("/api/import", json=payload, headers=headers)
    rows = client.get("/api/progress", headers=headers).json()
    assert rows[0]["percent"] == 90


def test_import_com_replace_sobrescreve(client):
    _, headers = start(client)
    client.post(
        "/api/progress",
        json={"module_id": "mat-soma", "percent": 90},
        headers=headers,
    )
    payload = {"version": 1, "progress": {"alfa-letra-a": 10}, "replace": True}
    client.post("/api/import", json=payload, headers=headers)
    ids = {row["module_id"] for row in client.get("/api/progress", headers=headers).json()}
    assert ids == {"alfa-letra-a"}


def test_import_versionado_e_limitado(client):
    _, headers = start(client)
    assert client.post("/api/import", json={"version": 99}, headers=headers).status_code == 422
    assert (
        client.post(
            "/api/import", json={"version": 1, "favorites": ["x"] * 501}, headers=headers
        ).status_code
        == 422
    )


def test_reset_apaga_so_os_dados_da_sessao(client):
    _, alice = start(client)
    _, bruno = start(client)
    client.post("/api/progress", json={"module_id": "mat-soma", "percent": 30}, headers=alice)
    client.post("/api/progress", json={"module_id": "mat-soma", "percent": 70}, headers=bruno)

    assert client.delete("/api/progress", headers=alice).json()["deleted"] == 1
    assert client.get("/api/progress", headers=alice).json() == []
    assert client.get("/api/progress", headers=bruno).json()[0]["percent"] == 70


def test_export_do_estudante_nao_inclui_outro(client):
    _, alice = start(client)
    _, bruno = start(client)
    client.post("/api/progress", json={"module_id": "mat-soma", "percent": 30}, headers=alice)
    exported = client.get("/api/export", headers=bruno).json()
    assert exported["progress"] == {}


# ── Sessão ──────────────────────────────────────────────────────────────


def test_sessao_devolve_aviso_de_privacidade_e_nao_pede_dados(client):
    r = client.post("/api/session")
    body = r.json()
    assert body["user"]["kind"] == "anonymous"
    assert "Não pedimos nome" in body["notice"]
    assert r.request.content in (b"", None)


def test_sessao_valida_responde_dados(client):
    _, headers = start(client)
    r = client.get("/api/session", headers=headers)
    assert r.status_code == 200
    assert r.json()["user"]["kind"] == "anonymous"


def test_sessao_anonima_nao_guarda_email(client):
    start(client)
    from api.main import app
    from api.database import get_db
    from api.models import User

    gen = app.dependency_overrides[get_db]()
    db = next(gen)
    try:
        users = db.query(User).all()
        assert users
        assert all(u.email is None and u.name is None for u in users)
    finally:
        gen.close()


def test_campos_extras_no_pedido_sao_rejeitados(client, no_llm):
    """Nada de mandar contexto pessoal escondido para o tutor."""
    r = client.post(
        "/api/tutor/ask",
        json={"message": "oi", "subject": "alfabetizacao", "user_id": 1, "email": "a@b.c"},
    )
    assert r.status_code == 422


def test_json_exportado_nao_contem_token(client):
    token, headers = start(client)
    client.post("/api/progress", json={"module_id": "mat-soma", "percent": 20}, headers=headers)
    raw = json.dumps(client.get("/api/export", headers=headers).json())
    assert token not in raw
