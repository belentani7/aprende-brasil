"""Guarda-corpo do conteúdo: nada de relleno e nada de palavra inventada.

A trilha de Alfabetização já foi gerada pegando as primeiras palavras do banco
aberto que começavam com cada letra, o que produzia exemplos como
"aabora, aac, aaiún". Estes testes travam o conteúdo curado atual: cada módulo
de letra, família silábica e tema precisa mostrar as palavras revisadas à mão.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.content_alfabetizacao import FAMILIAS, LETRAS, TEMAS

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "client" / "src" / "data" / "curriculum.json"
STEPS = ROOT / "client" / "src" / "data" / "curriculum-steps.json"

CURATED_TRACKS = {"informatica", "matematica", "idiomas"}
CURATED_MIN = 40
ALFA_MIN = 20

PLACEHOLDERS = [
    "Exemplo prático sobre",
    "no seu dia a dia",
    "Ótimo! Continue praticando",
    "Você conseguiu? O que foi mais difícil",
    "Agora é sua vez: pratique",
    "Veja este exemplo de",
    "Vamos aprender a",
    "Pratique com um exemplo real",
]

STEP_TYPES = ["explanation", "example", "practice", "check", "next"]


@pytest.fixture(scope="module")
def modules():
    if not CATALOG.exists():
        pytest.skip("curriculum.json ausente — rode: python3 scripts/export_static_curriculum.py")
    return json.loads(CATALOG.read_text(encoding="utf-8"))["modules"]


@pytest.fixture(scope="module")
def steps():
    if not STEPS.exists():
        pytest.skip("curriculum-steps.json ausente")
    return json.loads(STEPS.read_text(encoding="utf-8"))


def _texts(module_id: str, steps) -> list[str]:
    return [step["content"]["text"] for step in steps[module_id]]


def test_sem_placeholders(modules, steps):
    for m in modules:
        for texto in _texts(m["id"], steps):
            for marca in PLACEHOLDERS:
                assert marca not in texto, f"placeholder em {m['id']}: {marca!r}"


def test_conteudo_curado_tem_substancia(modules, steps):
    """Informática, Matemática e Idiomas: cada etapa precisa de texto real."""
    for m in modules:
        if m["track_id"] not in CURATED_TRACKS:
            continue
        for texto in _texts(m["id"], steps):
            assert len(texto.strip()) >= CURATED_MIN, f"{m['id']} com texto curto: {texto!r}"


def test_alfabetizacao_tem_texto(modules, steps):
    for m in modules:
        if m["track_id"] != "alfabetizacao":
            continue
        for texto in _texts(m["id"], steps):
            assert len(texto.strip()) >= ALFA_MIN, f"{m['id']} vazio"


def test_letras_usam_palavras_curadas(modules, steps):
    """Cada módulo de letra precisa mostrar pelo menos 3 palavras revisadas."""
    for letra, dados in LETRAS.items():
        module_id = f"alfa-letra-{letra}"
        example = _texts(module_id, steps)[1]
        presentes = [p for p in dados["palavras"] if p.lower() in example.lower()]
        assert len(presentes) >= 3, f"{module_id} sem palavras curadas: {example!r}"


def test_familias_silabicas_usam_palavras_curadas(modules, steps):
    for consoante, palavras in FAMILIAS.items():
        module_id = f"alfa-silaba-{consoante}"
        example = _texts(module_id, steps)[1]
        presentes = [p for p in palavras if p.lower() in example.lower()]
        assert len(presentes) >= 3, f"{module_id} sem palavras curadas: {example!r}"


def test_temas_usam_as_palavras_do_tema(modules, steps):
    for tid, _titulo, _tema, palavras in TEMAS:
        module_id = f"alfa-tema-{tid}"
        example = _texts(module_id, steps)[1]
        presentes = [p for p in palavras if p.lower() in example.lower()]
        assert len(presentes) >= 3, f"{module_id} sem palavras do tema: {example!r}"


def test_textos_do_dia_a_dia_tem_exemplo_real(modules, steps):
    for m in modules:
        if not m["id"].startswith("alfa-texto-"):
            continue
        example = _texts(m["id"], steps)[1]
        assert len(example.strip()) >= 80, f"{m['id']} sem exemplo real: {example!r}"


def test_explicacao_nao_repete_o_titulo(modules, steps):
    for m in modules:
        explicacao = steps[m["id"]][0]["content"]["text"]
        assert explicacao.strip() != f"{m['title']}: {m['subtitle']}", (
            f"explicação vazia em {m['id']}"
        )


def test_etapas_sao_distintas_por_modulo(modules, steps):
    for m in modules:
        textos = _texts(m["id"], steps)
        assert len(set(textos)) == len(textos), f"etapas repetidas em {m['id']}"


def test_tipos_de_etapa_completos(modules, steps):
    for m in modules:
        tipos = [s["type"] for s in steps[m["id"]]]
        assert tipos == STEP_TYPES, f"{m['id']} com etapas fora do padrão"
