import os

import httpx
from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/tutor", tags=["tutor"])

SUBJECT_LABELS = {
    "informatica": "informática",
    "matematica": "matemática",
    "idiomas": "idiomas",
    "alfabetizacao": "alfabetização",
}

NILO_SYSTEM = """Você é Nilo, o tutor da Aprende Brasil. Responda em português brasileiro, com tom acolhedor, curioso e objetivo. A pessoa está estudando {subject}. Explique uma ideia por vez, use exemplos concretos, faça no máximo uma pergunta de acompanhamento e nunca entregue uma resposta que substitua o raciocínio do aluno. Se for um exercício, ofereça uma pista antes da solução. Não invente progresso, notas ou informações pessoais. Mantenha a resposta em até 120 palavras."""

# Respostas locais (sem LLM) — úteis offline e como fallback.
LOCAL_RESPONSES = {
    "alfabetização": "Ótima pergunta! Vamos com calma: leia a palavra devagar, sílaba por sílaba. Qual parte você já reconhece?",
    "informática": "Boa pergunta! Vamos passo a passo. Qual parte do conceito parece mais confusa para você agora?",
    "matemática": "Vamos resolver juntos! Tente primeiro com números pequenos. O que acontece se você usar o número 2?",
    "idiomas": "Boa! Repita a frase em voz alta. Qual palavra soa diferente do que você esperava?",
}


class AskRequest(BaseModel):
    message: str = Field(min_length=1, max_length=800)
    subject: str = "alfabetizacao"


def _llm_config():
    """Configuração de LLM via variáveis de ambiente (OpenAI-compatível)."""
    url = os.environ.get("LLM_API_URL")
    key = os.environ.get("LLM_API_KEY")
    model = os.environ.get("LLM_MODEL", "gpt-4o-mini")
    return url, key, model


async def _ask_llm(message: str, subject_label: str) -> str | None:
    url, key, model = _llm_config()
    if not url or not key:
        return None
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                url,
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": NILO_SYSTEM.format(subject=subject_label)},
                        {"role": "user", "content": message},
                    ],
                    "temperature": 0.4,
                    "max_tokens": 300,
                },
            )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception:
        return None


@router.post("/ask")
async def ask_tutor(req: AskRequest):
    subject = SUBJECT_LABELS.get(req.subject, req.subject)
    answer = await _ask_llm(req.message, subject)
    if answer:
        return {"answer": answer, "source": "llm"}
    fallback = LOCAL_RESPONSES.get(
        subject, "Vamos explorar isso juntos: qual parte parece mais difícil para você agora?"
    )
    return {"answer": fallback, "source": "local"}


@router.get("/health")
def tutor_health():
    url, key, _ = _llm_config()
    return {"llm_configured": bool(url and key)}
