"""Sessão anônima opcional (sincronização entre aparelhos, sem cadastro)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from ..auth import SESSION_TTL, create_anonymous_session, get_session
from ..database import get_db
from ..limits import limiter
from ..models import UserSession

router = APIRouter(prefix="/api/session", tags=["session"])


@router.post("")
def start_session(request: Request, db: Session = Depends(get_db)):
    """Cria uma sessão anônima.

    Devolve o token **uma única vez**. Nenhum dado pessoal é pedido: o corpo
    desta requisição é vazio e o servidor não guarda IP, nome nem e-mail.
    """
    limiter.check(request, bucket="session", limit=10, window=3600)
    token, user, session = create_anonymous_session(db)
    return {
        "token": token,
        "user": {"id": user.id, "kind": "anonymous"},
        "expires_in_days": SESSION_TTL.days,
        "notice": (
            "Sessão anônima: guarde este código no seu aparelho. "
            "Não pedimos nome, e-mail nem CPF."
        ),
    }


@router.get("")
def read_session(session: UserSession = Depends(get_session)):
    """Confirma que a sessão do cabeçalho é válida e informa o vencimento."""
    return {
        "user": {"id": session.user_id, "kind": "anonymous"},
        "created_at": session.created_at,
        "last_seen_at": session.last_seen_at,
        "expires_at": session.expires_at,
    }
