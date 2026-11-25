"""Contrato das atividades interativas e validação no build.

Uma etapa deixa de ser só um texto e passa a poder carregar ``activities``
dentro de ``content``. O contrato é **retrocompatível**: etapas sem atividades
continuam válidas, e os campos antigos (``text``) não mudam.

```python
Activity = (
    multiple-choice | true-false | fill-blank |
    ordering | matching | numeric
)
```

Duas responsabilidades:

1. ``validate_activity`` / ``validate_content`` — falham o build quando uma
   atividade está malformada (opção certa inexistente, gabarito repetido,
   tolerância negativa, par vazio…). Melhor quebrar o build que publicar
   exercício errado.
2. Os construtores usados por ``scripts/activities_by_module.py`` conferem a
   aritmética do gabarito antes de gerar a atividade: nenhum ``numeric`` entra
   no currículo com resposta calculada à mão sem verificação.

Nada aqui depende de FastAPI nem de Node: é conteúdo, não aplicação.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any, Iterable

KINDS = {
    "multiple-choice",
    "true-false",
    "fill-blank",
    "ordering",
    "matching",
    "numeric",
}

MAX_ACTIVITIES_PER_STEP = 4
MAX_OPTIONS = 6
MAX_ITEMS = 8
MAX_PAIRS = 6


class ActivityError(ValueError):
    """Atividade inválida — interrompe o build."""


# ── Normalização de respostas de texto ───────────────────────────────────


def normalize_answer(value: str) -> str:
    """Compara respostas ignorando caixa, acentos, pontuação e espaço extra.

    é o que a interface faz ao comparar ``fill-blank``: assim "Amanhã", "amanha"
    e "  amanhã! " contam como a mesma resposta.
    """
    decomposed = unicodedata.normalize("NFD", value.strip().lower())
    without_marks = "".join(
        ch for ch in decomposed if unicodedata.category(ch) != "Mn"
    )
    cleaned = re.sub(r"[^\w\s]", "", without_marks, flags=re.UNICODE)
    return re.sub(r"\s+", " ", cleaned).strip()


# ── Validadores ──────────────────────────────────────────────────────────


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ActivityError(message)


def _require_text(value: Any, field: str, min_len: int = 3) -> None:
    _require(isinstance(value, str), f"{field}: precisa ser texto")
    _require(len(value.strip()) >= min_len, f"{field}: curto demais")


def validate_activity(activity: dict, *, path: str = "activity") -> None:
    _require(isinstance(activity, dict), f"{path}: precisa ser objeto")
    kind = activity.get("kind")
    _require(kind in KINDS, f"{path}: kind inválido {kind!r}")

    activity_id = activity.get("id")
    _require(isinstance(activity_id, str) and activity_id.strip(), f"{path}: id ausente")
    _require(
        re.fullmatch(r"[a-z0-9][a-z0-9-]{2,63}", activity_id) is not None,
        f"{path}: id deve ser slug minúsculo (a-z, 0-9, -)",
    )
    _require_text(activity.get("prompt"), f"{path}.prompt", min_len=8)

    if kind == "multiple-choice":
        options = activity.get("options")
        _require(
            isinstance(options, list) and 2 <= len(options) <= MAX_OPTIONS,
            f"{path}: 2 a {MAX_OPTIONS} opções",
        )
        for i, option in enumerate(options):
            _require_text(option, f"{path}.options[{i}]", min_len=1)
        _require(
            len(set(options)) == len(options), f"{path}: opções repetidas"
        )
        correct = activity.get("correctIndex")
        _require(
            isinstance(correct, int) and not isinstance(correct, bool),
            f"{path}: correctIndex precisa ser inteiro",
        )
        _require(0 <= correct < len(options), f"{path}: correctIndex fora das opções")
        _require_text(activity.get("explanation"), f"{path}.explanation", min_len=10)

    elif kind == "true-false":
        _require(
            isinstance(activity.get("answer"), bool), f"{path}: answer precisa ser booleano"
        )
        _require_text(activity.get("explanation"), f"{path}.explanation", min_len=10)

    elif kind == "fill-blank":
        accepted = activity.get("acceptedAnswers")
        _require(
            isinstance(accepted, list) and 1 <= len(accepted) <= 8,
            f"{path}: 1 a 8 respostas aceitas",
        )
        normalized = set()
        for i, answer in enumerate(accepted):
            _require_text(answer, f"{path}.acceptedAnswers[{i}]", min_len=1)
            key = normalize_answer(answer)
            # "A" e "a" são a mesma resposta: duas variantes de caixa não contam
            # como alternativas diferentes.
            _require(key not in normalized, f"{path}: resposta aceita repetida ({answer!r})")
            normalized.add(key)
        _require_text(activity.get("explanation"), f"{path}.explanation", min_len=10)

    elif kind == "ordering":
        items = activity.get("items")
        _require(
            isinstance(items, list) and 2 <= len(items) <= MAX_ITEMS,
            f"{path}: 2 a {MAX_ITEMS} itens",
        )
        for i, item in enumerate(items):
            _require_text(item, f"{path}.items[{i}]", min_len=1)
        order = activity.get("correctOrder")
        _require(
            isinstance(order, list) and len(order) == len(items),
            f"{path}: correctOrder precisa cobrir todos os itens",
        )
        _require(
            sorted(order) == list(range(len(items))),
            f"{path}: correctOrder deve ser permutação de 0..n-1",
        )

    elif kind == "matching":
        pairs = activity.get("pairs")
        _require(
            isinstance(pairs, list) and 2 <= len(pairs) <= MAX_PAIRS,
            f"{path}: 2 a {MAX_PAIRS} pares",
        )
        lefts, rights = set(), set()
        for i, pair in enumerate(pairs):
            _require(isinstance(pair, dict), f"{path}.pairs[{i}]: precisa ser objeto")
            _require_text(pair.get("left"), f"{path}.pairs[{i}].left", min_len=1)
            _require_text(pair.get("right"), f"{path}.pairs[{i}].right", min_len=1)
            lefts.add(pair["left"])
            rights.add(pair["right"])
        _require(len(lefts) == len(pairs), f"{path}: lados esquerdos repetidos")
        _require(len(rights) == len(pairs), f"{path}: lados direitos repetidos")
        _require_text(activity.get("explanation", ""), f"{path}.explanation", min_len=0)

    elif kind == "numeric":
        answer = activity.get("answer")
        _require(
            isinstance(answer, (int, float)) and not isinstance(answer, bool),
            f"{path}: answer precisa ser número",
        )
        tolerance = activity.get("tolerance")
        _require(
            isinstance(tolerance, (int, float))
            and not isinstance(tolerance, bool)
            and tolerance >= 0,
            f"{path}: tolerance precisa ser >= 0",
        )
        _require(
            isinstance(activity.get("unit", ""), str), f"{path}: unit precisa ser texto"
        )
        _require_text(activity.get("explanation"), f"{path}.explanation", min_len=10)


def validate_content(content: dict, *, path: str = "content") -> None:
    """Valida ``StepData.content`` (texto + campos opcionais + atividades)."""
    _require(isinstance(content, dict), f"{path}: content precisa ser objeto")
    _require_text(content.get("text"), f"{path}.text", min_len=10)

    for field in ("objectives", "examples", "references"):
        value = content.get(field)
        if value is not None:
            _require(isinstance(value, list), f"{path}.{field}: precisa ser lista")
            for i, item in enumerate(value):
                _require_text(item, f"{path}.{field}[{i}]", min_len=3)

    vocabulary = content.get("vocabulary")
    if vocabulary is not None:
        _require(isinstance(vocabulary, list), f"{path}.vocabulary: precisa ser lista")
        for i, entry in enumerate(vocabulary):
            _require(isinstance(entry, dict), f"{path}.vocabulary[{i}]: objeto")
            _require_text(entry.get("term"), f"{path}.vocabulary[{i}].term", min_len=1)
            _require_text(
                entry.get("definition"), f"{path}.vocabulary[{i}].definition", min_len=3
            )

    activities = content.get("activities")
    if activities is None:
        return
    _require(
        isinstance(activities, list) and len(activities) <= MAX_ACTIVITIES_PER_STEP,
        f"{path}.activities: no máximo {MAX_ACTIVITIES_PER_STEP}",
    )
    seen: set[str] = set()
    for i, activity in enumerate(activities):
        sub_path = f"{path}.activities[{i}]"
        validate_activity(activity, path=sub_path)
        activity_id = activity["id"]
        _require(activity_id not in seen, f"{path}: id de atividade repetido {activity_id}")
        seen.add(activity_id)


# ── Construtores com gabarito verificado ─────────────────────────────────


def multiple_choice(
    activity_id: str,
    prompt: str,
    options: list[str],
    correct: str,
    explanation: str,
) -> dict:
    """Cria um múltipla-escolha a partir da **resposta certa**, não do índice.

    Assim é impossível registrar o índice errado: a posição é calculada aqui.
    """
    _require(correct in options, f"{activity_id}: resposta correta não está nas opções")
    return {
        "kind": "multiple-choice",
        "id": activity_id,
        "prompt": prompt,
        "options": options,
        "correctIndex": options.index(correct),
        "explanation": explanation,
    }


def true_false(activity_id: str, prompt: str, answer: bool, explanation: str) -> dict:
    return {
        "kind": "true-false",
        "id": activity_id,
        "prompt": prompt,
        "answer": bool(answer),
        "explanation": explanation,
    }


def fill_blank(
    activity_id: str, prompt: str, accepted: Iterable[str], explanation: str
) -> dict:
    answers = list(accepted)
    return {
        "kind": "fill-blank",
        "id": activity_id,
        "prompt": prompt,
        "acceptedAnswers": answers,
        "explanation": explanation,
    }


def ordering(activity_id: str, prompt: str, items: list[str]) -> dict:
    """Recebe os itens **já na ordem correta**: o gabarito é a identidade."""
    return {
        "kind": "ordering",
        "id": activity_id,
        "prompt": prompt,
        "items": items,
        "correctOrder": list(range(len(items))),
    }


def matching(activity_id: str, prompt: str, pairs: list[tuple[str, str]],
             explanation: str = "") -> dict:
    return {
        "kind": "matching",
        "id": activity_id,
        "prompt": prompt,
        "pairs": [{"left": left, "right": right} for left, right in pairs],
        "explanation": explanation,
    }


def numeric_checked(
    activity_id: str,
    prompt: str,
    expression: str,
    explanation: str,
    *,
    tolerance: float = 0.01,
    unit: str = "",
    namespace: dict | None = None,
) -> dict:
    """Avalia a expressão em Python e usa o resultado como gabarito.

    ``expression`` é avaliada com ``eval`` restrito (sem builtins e com uma
    lista branca de nomes matemáticos), o que mantém a verificação simples e
    determinística. Qualquer erro de sintaxe ou nome desconhecido quebra o build.
    """
    safe = {"__builtins__": {}, "round": round, "abs": abs, "min": min, "max": max}
    if namespace:
        safe.update(namespace)
    try:
        value = eval(expression, safe)  # noqa: S307 - expressão de build confiável
    except Exception as exc:  # pragma: no cover - falha de build
        raise ActivityError(
            f"{activity_id}: expressão inválida {expression!r} ({exc})"
        ) from exc
    _require(
        isinstance(value, (int, float)) and not isinstance(value, bool),
        f"{activity_id}: expressão não devolveu número",
    )
    rounded = round(float(value), 4)
    if rounded == int(rounded):
        rounded = int(rounded)
    return {
        "kind": "numeric",
        "id": activity_id,
        "prompt": prompt,
        "answer": rounded,
        "tolerance": tolerance,
        "unit": unit,
        "explanation": explanation,
    }


def check_numeric(activity: dict, value: float) -> bool:
    """Mesma regra de correção usada pela interface (tolerância inclusiva)."""
    answer = activity["answer"]
    tolerance = activity.get("tolerance", 0)
    return abs(float(value) - float(answer)) <= tolerance + 1e-9
