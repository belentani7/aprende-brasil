"""Sessões anônimas para o campus remoto.

Decisões de privacidade (LGPD, minimização de dados):

- **O campus funciona sem conta.** O modo padrão do site é 100% local
  (`localStorage`), sem chamadas ao backend e sem cadastro.
- Quando alguém opta por sincronizar, o servidor cria uma **sessão anônima**:
  nenhum nome, e-mail, telefone ou documento é solicitado ou armazenado. O
  único dado pessoal envolvido é o token, que fica no aparelho da pessoa.
- O banco guarda apenas o **hash SHA-256** do token. Quem lê o SQLite não
  consegue reconstruir o token e, portanto, não consegue se passar pela pessoa.
- A identidade usada por progresso, favoritos, estatísticas e exportação é
  **sempre** a da sessão autenticada. `user_id` vindo do corpo, da query string
  ou de um header arbitrário é ignorado (e rejeitado pelos schemas).
"""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from .database import get_db
from .models import User, UserSession

# Tempo de vida da sessão. Deslizante: cada uso válido renova o prazo, de modo
# que uma pessoa que estuda toda semana não é deslogada no meio do curso.
SESSION_TTL = timedelta(days=180)

BEARER_PREFIX = "bearer "


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _as_utc(value: datetime | None) -> datetime | None:
    """SQLite devolve datetime sem timezone; normaliza para comparação segura."""
    if value is None:
        return None
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


def create_anonymous_session(db: Session) -> tuple[str, User, UserSession]:
    """Cria uma sessão anônima e devolve ``(token, user, session)``.

    O token em texto puro existe só nesta resposta: depois disso apenas o hash
    vive no banco. Chamar de novo gera uma sessão independente (outro espaço de
    progresso), o que também serve para testes de isolamento.
    """
    token = secrets.token_urlsafe(32)
    now = _utcnow()
    user = User(role="student", name=None, email=None)
    db.add(user)
    db.flush()
    session = UserSession(
        user_id=user.id,
        token_hash=hash_token(token),
        created_at=now,
        last_seen_at=now,
        expires_at=now + SESSION_TTL,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return token, user, session


def _token_from_request(request: Request) -> str | None:
    header = request.headers.get("authorization")
    if not header:
        return None
    value = header.strip()
    if value.lower().startswith(BEARER_PREFIX):
        token = value[len(BEARER_PREFIX) :].strip()
        return token or None
    return None


def get_session(request: Request, db: Session = Depends(get_db)) -> UserSession:
    """Dependência de autenticação: 401 se não houver sessão válida.

    Nenhuma rota aceita identidade vinda de query string ou corpo. Sem este
    cabeçalho, a rota remota simplesmente não responde dados de ninguém.
    """
    token = _token_from_request(request)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticação necessária",
            headers={"WWW-Authenticate": "Bearer"},
        )

    session = (
        db.query(UserSession)
        .filter(UserSession.token_hash == hash_token(token))
        .first()
    )
    now = _utcnow()

    if session is None or session.revoked_at is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sessão inválida",
            headers={"WWW-Authenticate": "Bearer"},
        )

    expires_at = _as_utc(session.expires_at)
    if expires_at is not None and expires_at <= now:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sessão expirada",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Renovação deslizante, gravada no máximo uma vez por dia para não escrever
    # no SQLite a cada requisição.
    last_seen = _as_utc(session.last_seen_at)
    if last_seen is None or now - last_seen > timedelta(days=1):
        session.last_seen_at = now
        session.expires_at = now + SESSION_TTL
        db.commit()

    return session


def require_student(session: UserSession = Depends(get_session)) -> int:
    """Identidade canônica do estudante autenticado (apenas o id interno)."""
    return session.user_id


def current_user_id(session: UserSession = Depends(get_session)) -> int:
    return session.user_id
