"""Especificações de aprendizagem por módulo (objetivos + atividades).

Cada entrada é ``SPECS[module_id] = ModuleSpec(objectives=[...], activities=[...])``.

Regras editoriais:

- As atividades usam **as mesmas palavras e textos** que a etapa da trilha já
  mostra. Nada de vocabulário novo sem explicação.
- Todo gabarito numérico vem de ``numeric_checked`` (expressão avaliada no
  build), nunca de conta feita à mão.
- Cada módulo tem pelo menos duas atividades de tipos diferentes, para que a
  pessoa reconheça, produza e confira — não só reconheça.
- Português brasileiro natural; nada de tradução literal do espanhol.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from scripts.activities import (
    fill_blank,
    matching,
    multiple_choice,
    numeric_checked,
    ordering,
    true_false,
)


@dataclass
class ModuleSpec:
    objectives: list[str]
    activities: list[dict] = field(default_factory=list)
    # Onde as atividades aparecem: a etapa de prática por padrão.
    place: str = "practice"


def spec(objectives: list[str], activities: list[dict], place: str = "practice") -> ModuleSpec:
    return ModuleSpec(objectives=list(objectives), activities=list(activities), place=place)


__all__ = [
    "ModuleSpec",
    "spec",
    "fill_blank",
    "matching",
    "multiple_choice",
    "numeric_checked",
    "ordering",
    "true_false",
]
