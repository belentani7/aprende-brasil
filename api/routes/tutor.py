"""Tutor Nilo no servidor.

Arquitetura:

- **Local (padrão).** Responde a partir do conteúdo real do currículo no
  SQLite: recupera as etapas do módulo mais próximo e devolve um roteiro
  pedagógico. Funciona sem rede, sem custo e sem enviar nada a terceiros.
- **Generativo (desligado por padrão).** Só é usado quando *todas* as condições
  abaixo são verdadeiras:
    1. ``LLM_ENABLED=1`` (autorização explícita de quem opera o servidor);
    2. ``LLM_API_URL`` e ``LLM_API_KEY`` configurados no backend;
    3. o cliente não estourou o limite de uso nem o orçamento diário;
    4. o provedor respondeu dentro do timeout.

Proteções do modo generativo: mensagem truncada, contexto limitado ao módulo
consultado, nenhuma identidade do estudante no payload, timeout curto,
concorrência máxima, teto de caracteres por dia e *fallback* local em qualquer
erro. A resposta generativa é marcada com ``source: "llm"`` para que a interface
avise que aquele texto não foi escrito por humanos.
"""

from __future__ import annotations

import asyncio
import os
import re
import unicodedata
from dataclasses import dataclass, field
from datetime import date

import httpx
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from ..database import get_db
from ..limits import limiter
from ..models import Module, ModuleStep

router = APIRouter(prefix="/api/tutor", tags=["tutor"])

SUBJECT_LABELS = {
    "informatica": "informática",
    "matematica": "matemática",
    "idiomas": "idiomas",
    "alfabetizacao": "alfabetização",
}

TRACK_LABELS = {
    "informatica": "Informática",
    "matematica": "Matemática",
    "idiomas": "Idiomas",
    "alfabetizacao": "Alfabetização",
}

NILO_SYSTEM = """Você é Nilo, tutor da Aprende Brasil. Responda em português brasileiro, com tom acolhedor, curioso e objetivo. A pessoa está estudando {subject}. Explique uma ideia por vez, use exemplos concretos, faça no máximo uma pergunta de acompanhamento e nunca entregue uma resposta que substitua o raciocínio do aluno. Se for um exercício, ofereça uma pista antes da solução. Não invente progresso, notas ou informações pessoais. Mantenha a resposta em até 120 palavras.

Material do módulo atual (use como base factual, sem copiar o texto literal):
{context}"""

# ── Limites do modo generativo ───────────────────────────────────────────
LLM_TIMEOUT_SECONDS = float(os.environ.get("LLM_TIMEOUT_SECONDS", "12"))
LLM_DAILY_CHAR_BUDGET = int(os.environ.get("LLM_DAILY_CHAR_BUDGET", "200000"))
LLM_MAX_CONCURRENCY = int(os.environ.get("LLM_MAX_CONCURRENCY", "2"))
LLM_MAX_CONTEXT_CHARS = 1200
LLM_MAX_OUTPUT_TOKENS = 300
LLM_PER_IP_PER_HOUR = int(os.environ.get("LLM_PER_IP_PER_HOUR", "30"))


@dataclass
class _Budget:
    day: date = field(default_factory=date.today)
    chars: int = 0
    in_flight: int = 0


_budget = _Budget()


def _llm_config() -> tuple[str | None, str | None, str]:
    url = os.environ.get("LLM_API_URL")
    key = os.environ.get("LLM_API_KEY")
    model = os.environ.get("LLM_MODEL", "gpt-4o-mini")
    return url, key, model


def llm_allowed() -> bool:
    """Só liga o provedor externo com autorização explícita."""
    if os.environ.get("LLM_ENABLED") != "1":
        return False
    url, key, _ = _llm_config()
    return bool(url and key)


class AskRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: str = Field(min_length=1, max_length=800)
    subject: str = Field(default="alfabetizacao", max_length=32)
    module_id: str | None = Field(default=None, max_length=64)


# ── Motor local ──────────────────────────────────────────────────────────

LOCAL_GREETING = (
    "Oi! Sou o Nilo, o tutor da Aprende Brasil. Trabalho aqui mesmo, sem enviar "
    "suas perguntas para fora. Posso explicar um conceito, dar um exemplo, propor "
    "um exercício ou revisar o que você já estudou. Sobre o que você quer conversar?"
)


def _fold(text: str) -> str:
    """Minúsculas sem acento — para casar "porcentagem" com "Porcentágem"."""
    normalized = unicodedata.normalize("NFD", text.lower())
    return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")


STOPWORDS = {
    "que", "qual", "quais", "como", "quando", "onde", "porque", "para", "com",
    "sem", "dos", "das", "uma", "uns", "umas", "este", "esta", "isso", "meu",
    "minha", "seu", "sua", "nos", "nas", "nao", "sim", "mais", "menos", "tem",
    "ter", "esta", "estao", "ser", "sou", "sao", "foi", "era", "quero",
    "preciso", "posso", "pode", "explique", "explica", "ajuda", "ajudar",
    "entender", "aprender", "estudar", "favor", "voce", "tudo", "bem", "dia",
    "ola", "oi", "quero", "sobre", "ao", "os", "as", "em", "e", "ou", "de",
    "da", "do", "a", "o", "no", "na", "um", "se",
}


def _tokens(text: str) -> set[str]:
    words = re.findall(r"[a-z0-9]{3,}", _fold(text))
    return {w for w in words if w not in STOPWORDS}


def _search_modules(db: Session, message: str, subject: str, limit: int = 3):
    """Recuperação simples (TF por termos) sobre título, subtítulo e etapas."""
    terms = _tokens(message)
    track = subject if subject in TRACK_LABELS else None
    modules = db.query(Module)
    if track:
        modules = modules.filter(Module.track_id == track)
    candidates = modules.all()
    if not candidates:
        candidates = db.query(Module).all()

    scored: list[tuple[int, Module]] = []
    for module in candidates:
        haystack = _fold(f"{module.title} {module.subtitle or ''}")
        for step in module.steps:
            haystack += " " + _fold(step.content_json or "")
        score = sum(1 for term in terms if term in haystack)
        if score:
            title_hits = sum(1 for term in terms if term in _fold(module.title))
            scored.append((score + title_hits * 2, module))

    scored.sort(key=lambda pair: (-pair[0], pair[1].level_order, pair[1].title))
    picked = [module for _score, module in scored[:limit]]

    # Se a trilha atual não tem nada sobre o assunto, procura no currículo
    # inteiro: quem pergunta "como somo?" dentro de Alfabetização merece o
    # módulo de Matemática, não um "não encontrei".
    if not picked and track:
        return _search_modules(db, message, "", limit)

    return picked


def _step(module: Module, step_type: str) -> str:
    for step in module.steps:
        if step.step_type == step_type:
            import json

            try:
                data = json.loads(step.content_json or "{}")
            except ValueError:
                return ""
            return str(data.get("text", "")).strip()
    return ""


def local_answer(message: str, subject: str, module: Module | None) -> str:
    if re.fullmatch(r"\s*(oi|olá|ola|bom dia|boa tarde|boa noite|e aí|eai)[!. ]*\s*", _fold(message)):
        return LOCAL_GREETING

    if module is None:
        label = SUBJECT_LABELS.get(subject, subject)
        return (
            f"Ainda não achei um módulo de {label} que combine com essa pergunta. "
            "Tente escrever o assunto com outras palavras (por exemplo: "
            "\"somar dinheiro\", \"ler bula\", \"senha segura\") — assim eu encontro "
            "o material exato. Enquanto isso, uma boa estratégia: anote o que você "
            "já sabe e o ponto exato onde travou. Essa anotação vale mais que a "
            "resposta pronta."
        )

    concept = _step(module, "explanation")
    example = _step(module, "example")
    practice = _step(module, "practice")
    check = _step(module, "check")

    return "\n".join(
        [
            f"Vamos com {module.title.lower()}.",
            "",
            "O conceito, sem rodeios:",
            concept or module.subtitle or "",
            "",
            "Um exemplo concreto:",
            example or "Escolha um caso pequeno do seu dia e aplique a ideia uma vez.",
            "",
            "Agora tente você:",
            practice or "Refaça o exemplo mudando os números ou as palavras.",
            "",
            "Como conferir:",
            check or "Explique em voz alta o que você fez. Se conseguir explicar, aprendeu.",
            "",
            f"Isso vem do módulo “{module.title}” ({TRACK_LABELS.get(module.track_id, module.track_id)}). "
            "Quer que eu detalhe uma dessas partes?",
        ]
    )


# ── Modo generativo (opcional e limitado) ────────────────────────────────


def _budget_available(chars: int) -> bool:
    today = date.today()
    if _budget.day != today:
        _budget.day = today
        _budget.chars = 0
    return _budget.chars + chars <= LLM_DAILY_CHAR_BUDGET


async def _ask_llm(message: str, subject_label: str, context: str) -> str | None:
    url, key, model = _llm_config()
    if not url or not key or not llm_allowed():
        return None
    if _budget.in_flight >= LLM_MAX_CONCURRENCY:
        return None

    prompt_chars = len(message) + len(context)
    if not _budget_available(prompt_chars):
        return None

    _budget.in_flight += 1
    try:
        async with httpx.AsyncClient(timeout=LLM_TIMEOUT_SECONDS) as client:
            resp = await client.post(
                url,
                headers={
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [
                        {
                            "role": "system",
                            "content": NILO_SYSTEM.format(
                                subject=subject_label, context=context[:LLM_MAX_CONTEXT_CHARS]
                            ),
                        },
                        {"role": "user", "content": message},
                    ],
                    "temperature": 0.4,
                    "max_tokens": LLM_MAX_OUTPUT_TOKENS,
                },
            )
        resp.raise_for_status()
        data = resp.json()
        answer = str(data["choices"][0]["message"]["content"]).strip()
        _budget.chars += prompt_chars + len(answer)
        return answer or None
    except (httpx.HTTPError, KeyError, ValueError, IndexError, asyncio.TimeoutError):
        # Qualquer falha do provedor cai no motor local: a pessoa nunca fica sem
        # resposta por causa de um terceiro.
        return None
    finally:
        _budget.in_flight -= 1


@router.post("/ask")
async def ask_tutor(
    req: AskRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    subject_label = SUBJECT_LABELS.get(req.subject, req.subject)
    module = None
    if req.module_id:
        module = db.get(Module, req.module_id)
    if module is None:
        hits = _search_modules(db, req.message, req.subject, limit=1)
        module = hits[0] if hits else None

    if llm_allowed():
        limiter.check(request, bucket="tutor-llm", limit=LLM_PER_IP_PER_HOUR, window=3600)
        context = "\n".join(
            filter(
                None,
                [
                    f"Módulo: {module.title}" if module else "",
                    _step(module, "explanation") if module else "",
                    _step(module, "example") if module else "",
                ],
            )
        )
        answer = await _ask_llm(req.message, subject_label, context)
        if answer:
            return {"answer": answer, "source": "llm", "module_id": module.id if module else None}

    limiter.check(request, bucket="tutor-local", limit=120, window=3600)
    return {
        "answer": local_answer(req.message, req.subject, module),
        "source": "local",
        "module_id": module.id if module else None,
    }


@router.get("/health")
def tutor_health():
    url, key, _ = _llm_config()
    return {
        "llm_configured": bool(url and key),
        "llm_enabled": llm_allowed(),
        "engine": "llm" if llm_allowed() else "local",
        "daily_char_budget": LLM_DAILY_CHAR_BUDGET,
        "daily_char_used": _budget.chars,
    }
