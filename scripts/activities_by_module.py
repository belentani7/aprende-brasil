"""Une as atividades das quatro trilhas e injeta no conteúdo das etapas.

Este é o único ponto que sabe **onde** cada atividade mora:

- ``objectives`` vão para a etapa 1 (``explanation``), porque é ali que a pessoa
  decide se aquele módulo é o que ela procura.
- ``activities`` vão para a etapa de ``practice`` (a terceira), porque é a hora
  de tentar, errar e receber explicação — não de ler mais texto.

Nenhum texto existente é substituído: o conteúdo anterior continua em
``content["text"]``, e os campos novos são aditivos e opcionais no contrato.
"""

from __future__ import annotations

import json
from typing import Iterable

from scripts.activities import validate_content
from scripts import (
    specs_alfabetizacao,
    specs_idiomas,
    specs_informatica,
    specs_matematica,
)

TRACK_SPECS = {
    "alfabetizacao": specs_alfabetizacao.build(),
    "matematica": specs_matematica.build(),
    "informatica": specs_informatica.build(),
    "idiomas": specs_idiomas.build(),
}

SPECS: dict = {}
for _track, _specs in TRACK_SPECS.items():
    for _module_id, _spec in _specs.items():
        if _module_id in SPECS:  # pragma: no cover - erro de autoria
            raise AssertionError(f"módulo com especificação duplicada: {_module_id}")
        SPECS[_module_id] = _spec


def activity_count() -> int:
    return sum(len(spec.activities) for spec in SPECS.values())


def merged_content(module_id: str, step_type: str, text: str) -> dict:
    """Devolve ``content`` com objetivos/atividades quando existirem."""
    spec = SPECS.get(module_id)
    content: dict = {"text": text}
    if spec is None:
        return content

    if step_type == "explanation" and spec.objectives:
        content["objectives"] = list(spec.objectives)
    if step_type == spec.place and spec.activities:
        content["activities"] = list(spec.activities)
    return content


def content_json(module_id: str, step_type: str, text: str) -> str:
    content = merged_content(module_id, step_type, text)
    # Valida no momento da criação: um módulo novo sem atividades quebra aqui,
    # com o nome do módulo na mensagem de erro.
    validate_content(content, path=f"{module_id}/{step_type}")
    return json.dumps(content, ensure_ascii=False)


def check_coverage(module_ids: Iterable[str]) -> None:
    """Falha se algum módulo do currículo não tiver especificação própria."""
    ids = list(module_ids)
    missing = [module_id for module_id in ids if module_id not in SPECS]
    orphan = [module_id for module_id in SPECS if module_id not in set(ids)]
    problems = []
    if missing:
        problems.append(f"sem objetivos/atividades: {', '.join(missing[:10])}")
    if orphan:
        problems.append(f"especificação de módulo inexistente: {', '.join(orphan[:10])}")
    thin = [
        module_id
        for module_id in ids
        if module_id in SPECS and len(SPECS[module_id].activities) < 2
    ]
    if thin:
        problems.append(f"menos de 2 atividades: {', '.join(thin[:10])}")
    no_objectives = [
        module_id
        for module_id in ids
        if module_id in SPECS and len(SPECS[module_id].objectives) < 2
    ]
    if no_objectives:
        problems.append(f"menos de 2 objetivos: {', '.join(no_objectives[:10])}")
    if problems:
        raise AssertionError("Cobertura de atividades incompleta: " + " | ".join(problems))
