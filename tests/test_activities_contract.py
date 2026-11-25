"""Contrato das atividades e dos objetivos pedagógicos.

Estes testes são o equivalente Python do que o Vitest e a CLI já verificam. Eles
existem porque o conteúdo nasce em ``scripts/`` — um erro de autoria aqui chega
ao estudante sem passar por TypeScript nenhum.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from scripts import activities_by_module
from scripts.activities import ActivityError, validate_content

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "aprende.db"
STEPS_JSON = ROOT / "client" / "src" / "data" / "curriculum-steps.json"
KINDS = {
    "multiple-choice",
    "true-false",
    "fill-blank",
    "ordering",
    "matching",
    "numeric",
}


def _module_ids() -> list[str]:
    if DB.exists():
        import sqlite3

        conn = sqlite3.connect(DB)
        try:
            return [row[0] for row in conn.execute("select id from modules order by id")]
        finally:
            conn.close()
    return sorted(activities_by_module.SPECS)


def _all_activities():
    for module_id, spec in activities_by_module.SPECS.items():
        for activity in spec.activities:
            yield module_id, activity


def test_toda_trilha_tem_especificacao():
    assert set(activities_by_module.TRACK_SPECS) == {
        "alfabetizacao",
        "matematica",
        "informatica",
        "idiomas",
    }
    for track, specs in activities_by_module.TRACK_SPECS.items():
        assert specs, f"trilha {track} sem nenhuma especificação"


def test_check_coverage_passa_no_curriculo_real():
    # Se este teste falhar, o build falha antes de publicar: é de propósito.
    activities_by_module.check_coverage(_module_ids())


def test_check_coverage_rejeita_modulo_sem_atividade():
    with pytest.raises(AssertionError, match="sem objetivos/atividades"):
        activities_by_module.check_coverage([*_module_ids(), "modulo-que-nao-existe"])


def test_check_coverage_rejeita_modulo_com_uma_atividade_so(monkeypatch):
    module_id = _module_ids()[0]
    spec = activities_by_module.SPECS[module_id]
    monkeypatch.setattr(spec, "activities", spec.activities[:1], raising=False)
    with pytest.raises(AssertionError, match="menos de 2 atividades"):
        activities_by_module.check_coverage([module_id])


def test_nenhum_modulo_fica_sem_objetivos_ou_atividades():
    for module_id in _module_ids():
        spec = activities_by_module.SPECS[module_id]
        assert len(spec.objectives) >= 2, f"{module_id} tem menos de 2 objetivos"
        assert len(spec.activities) >= 2, f"{module_id} tem menos de 2 atividades"
        for objective in spec.objectives:
            assert len(objective.strip()) >= 12, f"{module_id}: objetivo raso"
            assert objective.strip().endswith((".", "!", "?")), (
                f"{module_id}: objetivo sem pontuação final"
            )


def test_total_de_atividades_e_o_publicado():
    count = activities_by_module.activity_count()
    assert count == sum(
        len(spec.activities) for spec in activities_by_module.SPECS.values()
    )
    assert count >= 400, "o currículo precisa de pelo menos 400 atividades"

    if not STEPS_JSON.exists():
        pytest.skip("currículo estático ausente — rode: npm run curriculum")

    published = json.loads(STEPS_JSON.read_text(encoding="utf-8"))
    found = 0
    modules_with_activities = 0
    for steps in published.values():
        module_activities = sum(
            len(step.get("content", {}).get("activities") or []) for step in steps
        )
        if module_activities:
            modules_with_activities += 1
        found += module_activities
    assert found == count, (
        "as atividades publicadas divergem das especificações — "
        "rode: npm run curriculum"
    )
    assert modules_with_activities == len(activities_by_module.SPECS)


def test_ids_de_atividade_sao_unicos():
    seen: dict[str, str] = {}
    for module_id, activity in _all_activities():
        previous = seen.get(activity["id"])
        assert previous is None, (
            f"id repetido: {activity['id']} ({previous} e {module_id})"
        )
        seen[activity["id"]] = module_id


def test_ids_de_atividade_sao_slug_valido():
    padrao = re.compile(r"[a-z0-9][a-z0-9-]{2,63}")
    for module_id, activity in _all_activities():
        assert padrao.fullmatch(activity["id"]), (
            f"{module_id}: id fora do padrão slug ({activity['id']})"
        )
        assert activity["id"].startswith(module_id.split("-")[0]), (
            f"{module_id}: id {activity['id']} sem relação com a trilha"
        )


def test_nenhuma_atividade_usa_placeholder():
    # "Todo"/"todos" são palavras legítimas em português; o marcador de tarefa
    # pendente é o "TODO" maiúsculo isolado, por isso a regex é sensível à caixa.
    proibidos = re.compile(
        r"(lorem ipsum|exemplo genérico|texto de exemplo|\bTODO\b|TODO:|xxx)"
    )
    for module_id, activity in _all_activities():
        assert len(activity["prompt"].strip()) >= 8, f"{module_id}: enunciado curto"
        assert not proibidos.search(activity["prompt"]), (
            f"{module_id}: enunciado genérico"
        )
        assert not proibidos.search(activity.get("explanation", "")), (
            f"{module_id}: explicação genérica"
        )


def test_todas_as_atividades_tem_explicacao_pedagogica():
    """Feedback não é opcional: é onde a pessoa entende o porquê."""
    for module_id, activity in _all_activities():
        assert activity["kind"] in KINDS
        if activity["kind"] in {"ordering", "matching"}:
            continue  # exercícios de manipulação; a etapa já explica o raciocínio
        assert len(activity.get("explanation", "").strip()) >= 10, (
            f"{module_id}: {activity['id']} sem explicação"
        )


def test_gabaritos_de_multipla_escolha_apontam_para_opcao_existente():
    for _module_id, activity in _all_activities():
        if activity["kind"] != "multiple-choice":
            continue
        options = activity["options"]
        assert len(set(options)) == len(options), f"{activity['id']}: opções repetidas"
        assert 0 <= activity["correctIndex"] < len(options), (
            f"{activity['id']}: índice de resposta fora da lista"
        )
        assert len(options) >= 3, f"{activity['id']}: menos de 3 alternativas"
        for option in options:
            assert option.strip(), f"{activity['id']}: alternativa vazia"


def test_numericas_tem_resposta_numerica_e_unidade():
    for _module_id, activity in _all_activities():
        if activity["kind"] != "numeric":
            continue
        answer = activity["answer"]
        assert isinstance(answer, (int, float)) and not isinstance(answer, bool), (
            f"{activity['id']}: resposta precisa ser número"
        )
        assert activity["tolerance"] >= 0
        assert isinstance(activity.get("unit", ""), str)
        assert activity.get("explanation"), f"{activity['id']}: sem explicação"


def test_numericas_batem_com_a_aritmetica_quando_o_enunciado_e_uma_conta():
    """Enunciados do tipo ``34 + 25 = ?`` são conferidos pela própria máquina."""
    conta = re.compile(
        r"^\s*(\d+(?:[.,]\d+)?)\s*([+−\-x×÷])\s*(\d+(?:[.,]\d+)?)\s*=\s*\?"
    )
    conferidas = 0
    for _module_id, activity in _all_activities():
        if activity["kind"] != "numeric":
            continue
        achado = conta.match(activity["prompt"])
        if not achado:
            continue
        a = float(achado.group(1).replace(",", "."))
        op = achado.group(2)
        b = float(achado.group(3).replace(",", "."))
        esperado = {
            "+": a + b,
            "−": a - b,
            "-": a - b,
            "x": a * b,
            "×": a * b,
            "÷": a / b if b else None,
        }[op]
        if esperado is None:
            continue
        assert abs(activity["answer"] - esperado) <= max(activity["tolerance"], 0.001), (
            f"{activity['id']}: {achado.group(0)} = {esperado}, "
            f"mas o gabarito diz {activity['answer']}"
        )
        conferidas += 1
    assert conferidas >= 1, "nenhuma conta numérica pôde ser conferida automaticamente"


def test_numeric_checked_rejeita_expressao_invalida():
    from scripts.activities import numeric_checked

    with pytest.raises(ActivityError):
        numeric_checked("x-1", "Quanto é 1 + 1?", "1 +", "Explicação suficientemente longa.")
    with pytest.raises(ActivityError):
        numeric_checked("x-2", "Quanto é 1 + 1?", "desconhecido * 2", "Explicação longa o bastante.")


def test_numeric_checked_confere_a_aritmetica_esperada():
    from scripts.activities import numeric_checked

    ok = numeric_checked(
        "x-3", "Quanto é 40 + 35?", "40 + 35", "40 + 35 = 75.", expected=75
    )
    assert ok["answer"] == 75

    with pytest.raises(ActivityError, match="não bate"):
        numeric_checked(
            "x-4", "Quanto é 40 + 35?", "40 + 30", "Conta errada.", expected=75
        )


def test_lacunas_tem_resposta_aceita_normalizada():
    for _module_id, activity in _all_activities():
        if activity["kind"] != "fill-blank":
            continue
        accepted = activity["acceptedAnswers"]
        assert accepted, f"{activity['id']}: sem respostas aceitas"
        for answer in accepted:
            assert answer == answer.strip(), (
                f"{activity['id']}: resposta com espaço sobrando"
            )
            assert answer, f"{activity['id']}: resposta vazia"


def test_ordenacao_e_associacao_tem_estrutura_valida():
    for _module_id, activity in _all_activities():
        if activity["kind"] == "ordering":
            items = activity["items"]
            assert len(items) >= 2, f"{activity['id']}: ordenação com 1 item"
            assert sorted(activity["correctOrder"]) == list(range(len(items))), (
                f"{activity['id']}: ordem inválida"
            )
        if activity["kind"] == "matching":
            pairs = activity["pairs"]
            assert len(pairs) >= 2, f"{activity['id']}: associação com 1 par"
            left = [pair["left"] for pair in pairs]
            right = [pair["right"] for pair in pairs]
            assert len(set(left)) == len(left), f"{activity['id']}: chave repetida"
            assert len(set(right)) == len(right), f"{activity['id']}: valor repetido"


def test_content_merge_e_retrocompativel():
    """O texto antigo continua no lugar; os campos novos são aditivos."""
    for module_id in _module_ids()[:5]:
        spec = activities_by_module.SPECS[module_id]
        content = activities_by_module.merged_content(
            module_id, "practice", "Texto da etapa que já existia no currículo."
        )
        assert content["text"] == "Texto da etapa que já existia no currículo."
        assert len(content["activities"]) == len(spec.activities)
        validate_content(content, path=module_id)

        explanation = activities_by_module.merged_content(
            module_id, "explanation", "Texto de abertura do módulo."
        )
        assert explanation["objectives"] == spec.objectives
        assert "activities" not in explanation


def test_validate_content_pega_gabarito_quebrado():
    ruim = {
        "text": "Texto suficientemente longo para passar na validação mínima.",
        "activities": [
            {
                "id": "x-1",
                "kind": "multiple-choice",
                "prompt": "Qual é a resposta correta desta pergunta?",
                "options": ["a", "b", "c"],
                "correctIndex": 9,
            }
        ],
    }
    with pytest.raises(ActivityError, match="correctIndex"):
        validate_content(ruim)


def test_validate_content_pega_atividade_repetida_no_mesmo_passo():
    atividade = {
        "id": "x-1",
        "kind": "true-false",
        "prompt": "O Sol nasce de manhã.",
        "answer": True,
        "explanation": "Sim, o Sol nasce a leste pela manhã.",
    }
    repetido = {
        "text": "Texto suficientemente longo para passar na validação mínima.",
        "activities": [atividade, dict(atividade)],
    }
    with pytest.raises(ActivityError, match="repetid"):
        validate_content(repetido)


def test_metadados_de_licenca_dos_dados_abertos():
    """Dados de terceiros entram com data, origem e licença registradas."""
    docs = ROOT / "client" / "public" / "open-data"
    assert docs.exists()
    readme = docs / "README.md"
    assert readme.exists(), "open-data precisa de um README com origem e licença"
    texto = readme.read_text(encoding="utf-8").lower()
    for campo in ("licen", "fonte", "data"):
        assert campo in texto, f"open-data/README.md sem campo '{campo}'"
