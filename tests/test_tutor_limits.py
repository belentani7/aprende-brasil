"""Tutor: o modo generativo é opt-in, limitado e nunca obrigatório.

Nenhum teste aqui faz chamada real de rede: o provedor é simulado para provar
os limites (orçamento, concorrência, timeout, fallback) e a marcação de origem.
"""

from __future__ import annotations

import httpx
import pytest

from api.routes import tutor as tutor_module


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    for var in ("LLM_API_URL", "LLM_API_KEY", "LLM_MODEL", "LLM_ENABLED"):
        monkeypatch.delenv(var, raising=False)
    tutor_module._budget.chars = 0
    tutor_module._budget.in_flight = 0


def _enable(monkeypatch):
    monkeypatch.setenv("LLM_API_URL", "https://llm.example/v1/chat")
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.setenv("LLM_ENABLED", "1")


def test_com_credenciais_mas_sem_autorizacao_nao_usa_llm(client, monkeypatch):
    monkeypatch.setenv("LLM_API_URL", "https://llm.example/v1/chat")
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    r = client.post("/api/tutor/ask", json={"message": "o que é soma?"})
    body = r.json()
    assert body["source"] == "local"
    assert client.get("/api/tutor/health").json()["llm_enabled"] is False


def test_llm_desligado_por_padrao(client):
    health = client.get("/api/tutor/health").json()
    assert health["engine"] == "local"
    assert health["llm_configured"] is False


def test_resposta_generativa_e_marcada_e_usa_contexto_do_modulo(client, monkeypatch):
    _enable(monkeypatch)
    sent: dict = {}

    class FakeAsyncClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc):
            return False

        async def post(self, url, headers=None, json=None):
            sent["url"] = url
            sent["payload"] = json
            return httpx.Response(
                200,
                json={"choices": [{"message": {"content": "Some juntando 2 e 3."}}]},
                request=httpx.Request("POST", url),
            )

    monkeypatch.setattr(tutor_module.httpx, "AsyncClient", FakeAsyncClient)

    r = client.post(
        "/api/tutor/ask",
        json={"message": "como somo?", "module_id": "mat-soma"},
    )
    body = r.json()
    assert body["source"] == "llm"
    assert body["module_id"] == "mat-soma"
    assert "2 e 3" in body["answer"]

    system_prompt = sent["payload"]["messages"][0]["content"]
    assert "mat-soma" not in system_prompt  # só título/texto, não ids internos
    assert sent["payload"]["max_tokens"] == tutor_module.LLM_MAX_OUTPUT_TOKENS


def test_falha_do_provedor_cai_no_motor_local(client, monkeypatch):
    _enable(monkeypatch)

    class Failing:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc):
            return False

        async def post(self, *args, **kwargs):
            raise httpx.ConnectTimeout("timeout")

    monkeypatch.setattr(tutor_module.httpx, "AsyncClient", Failing)
    r = client.post("/api/tutor/ask", json={"message": "o que é soma?"})
    assert r.status_code == 200
    assert r.json()["source"] == "local"


def test_orcamento_diario_esgotado_nao_chama_provedor(client, monkeypatch):
    _enable(monkeypatch)
    called = {"n": 0}

    class Spy:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc):
            return False

        async def post(self, *args, **kwargs):
            called["n"] += 1
            raise AssertionError("não deveria chamar o provedor")

    monkeypatch.setattr(tutor_module.httpx, "AsyncClient", Spy)
    tutor_module._budget.chars = tutor_module.LLM_DAILY_CHAR_BUDGET
    r = client.post("/api/tutor/ask", json={"message": "o que é soma?"})
    assert r.json()["source"] == "local"
    assert called["n"] == 0


def test_concorrencia_maxima_respeitada(monkeypatch):
    _enable(monkeypatch)
    tutor_module._budget.in_flight = tutor_module.LLM_MAX_CONCURRENCY
    import asyncio

    result = asyncio.run(tutor_module._ask_llm("oi", "alfabetização", "contexto"))
    assert result is None


def test_limitador_por_ip_do_tutor(client, monkeypatch):
    _enable(monkeypatch)
    monkeypatch.setattr(tutor_module, "LLM_PER_IP_PER_HOUR", 2)

    class Fake:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc):
            return False

        async def post(self, url, **kwargs):
            return httpx.Response(
                200,
                json={"choices": [{"message": {"content": "ok"}}]},
                request=httpx.Request("POST", url),
            )

    monkeypatch.setattr(tutor_module.httpx, "AsyncClient", Fake)
    assert client.post("/api/tutor/ask", json={"message": "a"}).status_code == 200
    assert client.post("/api/tutor/ask", json={"message": "b"}).status_code == 200
    r = client.post("/api/tutor/ask", json={"message": "c"})
    assert r.status_code == 429
    assert r.headers["Retry-After"].isdigit()


def test_payload_nao_leva_dados_pessoais(client, monkeypatch):
    _enable(monkeypatch)
    captured: dict = {}

    class Spy:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc):
            return False

        async def post(self, url, headers=None, json=None):
            captured.update(json)
            return httpx.Response(
                200,
                json={"choices": [{"message": {"content": "ok"}}]},
                request=httpx.Request("POST", url),
            )

    monkeypatch.setattr(tutor_module.httpx, "AsyncClient", Spy)
    token = client.post("/api/session").json()["token"]
    client.post(
        "/api/tutor/ask",
        json={"message": "como somo?", "module_id": "mat-soma"},
        headers={"Authorization": f"Bearer {token}"},
    )
    raw = str(captured)
    assert token not in raw
    assert "user" not in captured
    assert set(captured) == {"model", "messages", "temperature", "max_tokens"}


def test_mensagem_longa_e_recusada(client):
    r = client.post("/api/tutor/ask", json={"message": "a" * 801})
    assert r.status_code == 422


def test_motor_local_encontra_modulo_por_palavra(client, no_llm):
    r = client.post("/api/tutor/ask", json={"message": "quero aprender a somar"})
    body = r.json()
    assert body["module_id"] == "mat-soma"
    assert "somar com as mãos" in body["answer"].lower()
