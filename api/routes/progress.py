"""Rotas de progresso, favoritos, estatísticas e portabilidade de dados.

Regra de ouro: **a identidade vem exclusivamente da sessão autenticada**
(``Depends(get_session)``). Nenhum destes endpoints aceita ``user_id`` no corpo
ou na query string — os schemas usam ``extra="forbid"``, então uma tentativa de
enviar ``user_id`` devolve 422 em vez de ser silenciosamente ignorada.

O campus continua funcionando sem sessão: nesse caso o frontend nunca chama
estas rotas e guarda tudo no ``localStorage`` do aparelho.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..auth import get_session
from ..database import get_db
from ..models import Favorite, Module, ModuleStep, Progress, UserSession
from ..limits import limiter

router = APIRouter(prefix="/api", tags=["progress"])

MAX_MODULES_PER_IMPORT = 500


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _clean_completed(values: list[int], max_order: int) -> list[int]:
    """Mantém só ordens de etapa que existem no módulo, sem duplicatas."""
    return sorted({v for v in values if 1 <= v <= max_order})


class ProgressIn(BaseModel):
    """Corpo aceito ao salvar progresso — sem ``user_id`` de propósito."""

    model_config = ConfigDict(extra="forbid")

    module_id: str = Field(min_length=1, max_length=64)
    percent: float = Field(ge=0, le=100)
    completed: list[int] | None = Field(default=None, max_length=50)


class FavoriteIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    module_id: str = Field(min_length=1, max_length=64)


class ImportIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: int = Field(default=1, ge=1, le=1)
    progress: dict[str, float] = Field(default_factory=dict)
    completed: dict[str, list[int]] = Field(default_factory=dict)
    favorites: list[str] = Field(default_factory=list, max_length=MAX_MODULES_PER_IMPORT)
    # Importação é aditiva por padrão: nunca reduz o que a pessoa já conquistou.
    replace: bool = False
    # Campo informativo presente no arquivo exportado; aceito e ignorado.
    exported_at: str | None = None


def _module_or_404(db: Session, module_id: str) -> Module:
    module = db.get(Module, module_id)
    if module is None:
        raise HTTPException(status_code=404, detail="Módulo não encontrado")
    return module


def _step_count(db: Session, module_id: str) -> int:
    return db.query(ModuleStep).filter(ModuleStep.module_id == module_id).count() or 5


@router.get("/progress")
def list_progress(
    session: UserSession = Depends(get_session),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(Progress)
        .filter(Progress.user_id == session.user_id)
        .order_by(Progress.last_activity.desc())
        .all()
    )
    return [
        {
            "module_id": r.module_id,
            "percent": r.percent,
            "completed": json.loads(r.completed_json) if r.completed_json else [],
            "started_at": r.started_at,
            "last_activity": r.last_activity,
        }
        for r in rows
    ]


@router.post("/progress")
def save_progress(
    payload: ProgressIn,
    session: UserSession = Depends(get_session),
    db: Session = Depends(get_db),
):
    """Escrita idempotente e monotônica.

    Repetir a mesma requisição não duplica linha (restrição única) nem regride o
    percentual. A concorrência é tratada com ``IntegrityError``: se duas
    requisições criarem a linha ao mesmo tempo, a segunda relê a linha existente.
    """
    _module_or_404(db, payload.module_id)
    total = _step_count(db, payload.module_id)
    completed = (
        _clean_completed(payload.completed, total) if payload.completed else None
    )

    def apply(row: Progress) -> Progress:
        row.percent = max(row.percent or 0, payload.percent)
        row.last_activity = _now()
        if completed is not None:
            previous = set(json.loads(row.completed_json)) if row.completed_json else set()
            merged = sorted(previous | set(completed))
            row.completed_json = json.dumps(merged)
        return row

    row = (
        db.query(Progress)
        .filter(
            Progress.user_id == session.user_id,
            Progress.module_id == payload.module_id,
        )
        .first()
    )
    if row is None:
        row = Progress(
            user_id=session.user_id,
            module_id=payload.module_id,
            percent=payload.percent,
            completed_json=json.dumps(completed) if completed is not None else None,
            started_at=_now(),
            last_activity=_now(),
        )
        apply(row)
        db.add(row)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            row = (
                db.query(Progress)
                .filter(
                    Progress.user_id == session.user_id,
                    Progress.module_id == payload.module_id,
                )
                .one()
            )
            apply(row)
            db.commit()
    else:
        apply(row)
        db.commit()

    db.refresh(row)
    return {
        "ok": True,
        "module_id": row.module_id,
        "percent": row.percent,
        "completed": json.loads(row.completed_json) if row.completed_json else [],
    }


@router.get("/stats")
def stats(
    session: UserSession = Depends(get_session),
    db: Session = Depends(get_db),
):
    total = db.query(Module).count()
    rows = db.query(Progress).filter(Progress.user_id == session.user_id).all()
    done = sum(1 for r in rows if (r.percent or 0) >= 100)
    started = len(rows)
    avg = round(sum(r.percent or 0 for r in rows) / total, 1) if total else 0
    return {
        "total_modules": total,
        "started": started,
        "completed": done,
        "overall_percent": avg,
    }


@router.get("/favorites")
def list_favorites(
    session: UserSession = Depends(get_session),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(Favorite)
        .filter(Favorite.user_id == session.user_id)
        .order_by(Favorite.created_at)
        .all()
    )
    return [r.module_id for r in rows]


@router.post("/favorites")
def toggle_favorite(
    payload: FavoriteIn,
    session: UserSession = Depends(get_session),
    db: Session = Depends(get_db),
):
    _module_or_404(db, payload.module_id)
    row = (
        db.query(Favorite)
        .filter(
            Favorite.user_id == session.user_id,
            Favorite.module_id == payload.module_id,
        )
        .first()
    )
    if row is not None:
        db.delete(row)
        db.commit()
        return {"favorited": False, "module_id": payload.module_id}

    db.add(Favorite(user_id=session.user_id, module_id=payload.module_id))
    try:
        db.commit()
    except IntegrityError:
        # Duplo clique: o favorito já existe, então o estado final é "favoritado".
        db.rollback()
    return {"favorited": True, "module_id": payload.module_id}


@router.get("/export")
def export_data(
    session: UserSession = Depends(get_session),
    db: Session = Depends(get_db),
):
    """Exportação completa dos dados da própria sessão (portabilidade LGPD)."""
    rows = db.query(Progress).filter(Progress.user_id == session.user_id).all()
    favorites = [
        r.module_id
        for r in db.query(Favorite).filter(Favorite.user_id == session.user_id).all()
    ]
    return {
        "version": 1,
        "exported_at": _now().isoformat(),
        "progress": {r.module_id: r.percent for r in rows},
        "completed": {
            r.module_id: json.loads(r.completed_json)
            for r in rows
            if r.completed_json
        },
        "favorites": favorites,
    }


@router.post("/import")
def import_data(
    payload: ImportIn,
    session: UserSession = Depends(get_session),
    db: Session = Depends(get_db),
    request: Request = None,
):
    """Restaura um arquivo exportado. Aditivo por padrão; ``replace`` apaga antes."""
    limiter.check(request, bucket="import", limit=20, window=3600)

    known = {m[0] for m in db.query(Module.id).all()}
    if payload.replace:
        db.query(Progress).filter(Progress.user_id == session.user_id).delete()
        db.query(Favorite).filter(Favorite.user_id == session.user_id).delete()
        db.commit()

    imported = 0
    for module_id, percent in list(payload.progress.items())[:MAX_MODULES_PER_IMPORT]:
        if module_id not in known:
            continue
        total = _step_count(db, module_id)
        completed = _clean_completed(payload.completed.get(module_id, []), total)
        row = (
            db.query(Progress)
            .filter(
                Progress.user_id == session.user_id,
                Progress.module_id == module_id,
            )
            .first()
        )
        clamped = max(0.0, min(100.0, float(percent)))
        if row is None:
            db.add(
                Progress(
                    user_id=session.user_id,
                    module_id=module_id,
                    percent=clamped,
                    completed_json=json.dumps(completed) if completed else None,
                    started_at=_now(),
                    last_activity=_now(),
                )
            )
        else:
            row.percent = max(row.percent or 0, clamped) if not payload.replace else clamped
            previous = set(json.loads(row.completed_json)) if row.completed_json else set()
            merged = sorted(previous | set(completed))
            if merged:
                row.completed_json = json.dumps(merged)
            row.last_activity = _now()
        imported += 1

    existing = {
        r.module_id
        for r in db.query(Favorite).filter(Favorite.user_id == session.user_id).all()
    }
    for module_id in payload.favorites[:MAX_MODULES_PER_IMPORT]:
        if module_id in known and module_id not in existing:
            db.add(Favorite(user_id=session.user_id, module_id=module_id))

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Importação conflitante; tente novamente")

    return {"ok": True, "imported_modules": imported, "replaced": payload.replace}


@router.delete("/progress")
def reset_progress(
    session: UserSession = Depends(get_session),
    db: Session = Depends(get_db),
):
    """Reinício voluntário: apaga progresso e favoritos da sessão, não a sessão."""
    deleted = db.query(Progress).filter(Progress.user_id == session.user_id).delete()
    db.query(Favorite).filter(Favorite.user_id == session.user_id).delete()
    db.commit()
    return {"ok": True, "deleted": deleted}
