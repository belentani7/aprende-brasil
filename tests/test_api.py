"""Testes de contrato da API FastAPI (endpoint a endpoint)."""

from __future__ import annotations


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["project"] == "aprende-brasil"


def test_tracks_lista_com_contagem(client):
    r = client.get("/api/tracks")
    assert r.status_code == 200
    tracks = {t["id"]: t for t in r.json()}
    assert set(tracks) == {"alfabetizacao", "matematica"}
    assert tracks["alfabetizacao"]["module_count"] == 1
    assert tracks["matematica"]["module_count"] == 1


def test_modules_paginacao_e_total(client):
    r = client.get("/api/modules")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 2
    assert body["page"] == 1
    assert len(body["items"]) == 2

    r2 = client.get("/api/modules", params={"per_page": 1, "page": 2})
    assert r2.status_code == 200
    assert len(r2.json()["items"]) == 1


def test_modules_filtro_por_trilha(client):
    r = client.get("/api/modules", params={"track": "matematica"})
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 1
    assert body["items"][0]["id"] == "mat-soma"


def test_modules_busca(client):
    r = client.get("/api/modules", params={"search": "somar"})
    assert r.status_code == 200
    ids = [m["id"] for m in r.json()["items"]]
    assert ids == ["mat-soma"]


def test_modules_destaques(client):
    r = client.get("/api/modules/featured")
    assert r.status_code == 200
    assert [m["id"] for m in r.json()] == ["alfa-letra-a"]


def test_modules_per_page_invalido(client):
    assert client.get("/api/modules", params={"per_page": 0}).status_code == 422
    assert client.get("/api/modules", params={"page": 0}).status_code == 422


def test_module_detalhe_com_etapas_ordenadas(client):
    r = client.get("/api/modules/alfa-letra-a")
    assert r.status_code == 200
    body = r.json()
    assert body["id"] == "alfa-letra-a"
    assert [s["order"] for s in body["steps"]] == [1, 2, 3, 4, 5]
    assert [s["type"] for s in body["steps"]] == [
        "explanation", "example", "practice", "check", "next",
    ]
    assert body["steps"][0]["content"] == {"text": "texto 1"}


def test_module_inexistente_retorna_404(client):
    r = client.get("/api/modules/nao-existe")
    assert r.status_code == 404
    assert r.json()["detail"] == "Módulo não encontrado"


def test_tutor_fallback_local(client, no_llm):
    r = client.post("/api/tutor/ask", json={"message": "Como leio esta palavra?", "subject": "alfabetizacao"})
    assert r.status_code == 200
    body = r.json()
    assert body["source"] == "local"
    assert body["answer"]


def test_tutor_valida_mensagem_vazia(client):
    assert client.post("/api/tutor/ask", json={"message": ""}).status_code == 422


def test_tutor_health_sem_llm(client, no_llm):
    r = client.get("/api/tutor/health")
    assert r.status_code == 200
    body = r.json()
    assert body["llm_configured"] is False
    assert body["llm_enabled"] is False
    assert body["engine"] == "local"


def _session(client):
    body = client.post("/api/session").json()
    return {"Authorization": f"Bearer {body['token']}"}


def test_progresso_salva_e_nao_regride(client):
    headers = _session(client)
    payload = {"module_id": "alfa-letra-a", "percent": 40}
    assert client.post("/api/progress", json=payload, headers=headers).status_code == 200

    payload["percent"] = 20
    r = client.post("/api/progress", json=payload, headers=headers)
    assert r.status_code == 200
    assert r.json()["percent"] == 40

    rows = client.get("/api/progress", headers=headers).json()
    assert len(rows) == 1
    assert rows[0]["module_id"] == "alfa-letra-a"


def test_progresso_modulo_inexistente(client):
    headers = _session(client)
    r = client.post("/api/progress", json={"module_id": "x", "percent": 10}, headers=headers)
    assert r.status_code == 404


def test_progresso_percentual_invalido(client):
    headers = _session(client)
    r = client.post(
        "/api/progress", json={"module_id": "alfa-letra-a", "percent": 150}, headers=headers
    )
    assert r.status_code == 422


def test_stats(client):
    headers = _session(client)
    client.post("/api/progress", json={"module_id": "alfa-letra-a", "percent": 100}, headers=headers)
    r = client.get("/api/stats", headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert body["total_modules"] == 2
    assert body["started"] == 1
    assert body["completed"] == 1
    assert body["overall_percent"] == 50.0


def test_favoritos_toggle(client):
    headers = _session(client)
    assert client.get("/api/favorites", headers=headers).json() == []

    r = client.post("/api/favorites", json={"module_id": "mat-soma"}, headers=headers)
    assert r.json() == {"favorited": True, "module_id": "mat-soma"}
    assert client.get("/api/favorites", headers=headers).json() == ["mat-soma"]

    r = client.post("/api/favorites", json={"module_id": "mat-soma"}, headers=headers)
    assert r.json() == {"favorited": False, "module_id": "mat-soma"}
    assert client.get("/api/favorites", headers=headers).json() == []


def test_favorito_modulo_inexistente(client):
    headers = _session(client)
    r = client.post("/api/favorites", json={"module_id": "nada"}, headers=headers)
    assert r.status_code == 404
