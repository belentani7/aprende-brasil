"""Guarda-corpo: o currículo não pode voltar a ter texto de relleno.

O antigo `seed_topics` gerava frases genéricas para Informática, Matemática e
Idiomas ("Exemplo prático sobre X.", "Ótimo! Continue praticando."). Estes
testes falham se algum placeholder reaparecer ou se o conteúdo curado encolher.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
JSON = ROOT / "client" / "src" / "data" / "curriculum.json"

# Trilhas que antes eram geradas por template e agora têm conteúdo curado.
CURATED_TRACKS = {"informatica", "matematica", "idiomas"}
CURATED_MIN = 40
ALFA_MIN = 20

PLACEHOLDERS = [
    "Exemplo prático sobre",
    "no seu dia a dia",
    "Ótimo! Continue praticando",
    "Você conseguiu? O que foi mais difícil",
    "Agora é sua vez: pratique",
]

STEP_TYPES = ["explanation", "example", "practice", "check", "next"]


@pytest.fixture(scope="module")
def modules():
    if not JSON.exists():
        pytest.skip("curriculum.json ausente — rode: python -m scripts.export_curriculum")
    return json.loads(JSON.read_text(encoding="utf-8"))["modules"]


def test_sem_placeholders(modules):
    for m in modules:
        for s in m["steps"]:
            texto = s["content"]["text"]
            for marca in PLACEHOLDERS:
                assert marca not in texto, f"placeholder em {m['id']}: {marca!r}"


def test_conteudo_curado_tem_substancia(modules):
    """Informática, Matemática e Idiomas: cada etapa precisa de texto real."""
    for m in modules:
        if m["track_id"] not in CURATED_TRACKS:
            continue
        for s in m["steps"]:
            texto = s["content"]["text"].strip()
            assert len(texto) >= CURATED_MIN, (
                f"{m['id']}/{s['type']} com {len(texto)} chars: {texto!r}"
            )


def test_alfabetizacao_tem_texto(modules):
    for m in modules:
        if m["track_id"] != "alfabetizacao":
            continue
        for s in m["steps"]:
            texto = s["content"]["text"].strip()
            assert len(texto) >= ALFA_MIN, f"{m['id']}/{s['type']} vazio"


def test_explicacao_nao_repete_o_titulo(modules):
    for m in modules:
        explicacao = next(s for s in m["steps"] if s["type"] == "explanation")
        assert explicacao["content"]["text"].strip() != f"{m['title']}: {m['subtitle']}", (
            f"explicação vazia em {m['id']}"
        )


def test_etapas_sao_distintas_por_modulo(modules):
    for m in modules:
        textos = [s["content"]["text"] for s in m["steps"]]
        assert len(set(textos)) == len(textos), f"etapas repetidas em {m['id']}"


def test_tipos_de_etapa_completos(modules):
    for m in modules:
        tipos = [s["type"] for s in m["steps"]]
        assert tipos == STEP_TYPES, f"{m['id']} com etapas fora do padrão"
