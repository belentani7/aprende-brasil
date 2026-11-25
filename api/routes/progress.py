from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from ..database import get_db
from ..models import Module, Progress, Favorite, User

router = APIRouter(prefix="/api", tags=["progress"])

DEFAULT_USER = 1


def _ensure_user(db: Session, user_id: int) -> User:
    user = db.get(User, user_id)
    if not user:
        user = User(id=user_id, name=f"Estudante {user_id}", role="student")
        db.add(user)
        db.commit()
    return user


class ProgressIn(BaseModel):
    user_id: int = DEFAULT_USER
    module_id: str = Field(min_length=1, max_length=64)
    percent: float = Field(ge=0, le=100)


class FavoriteIn(BaseModel):
    user_id: int = DEFAULT_USER
    module_id: str = Field(min_length=1, max_length=64)


@router.get("/progress")
def list_progress(user_id: int = DEFAULT_USER, db: Session = Depends(get_db)):
    rows = db.query(Progress).filter(Progress.user_id == user_id).all()
    return [
        {
            "module_id": r.module_id,
            "percent": r.percent,
            "started_at": r.started_at,
            "last_activity": r.last_activity,
        }
        for r in rows
    ]


@router.post("/progress")
def save_progress(payload: ProgressIn, db: Session = Depends(get_db)):
    if not db.get(Module, payload.module_id):
        raise HTTPException(status_code=404, detail="Módulo não encontrado")
    _ensure_user(db, payload.user_id)
    row = (
        db.query(Progress)
        .filter(Progress.user_id == payload.user_id, Progress.module_id == payload.module_id)
        .first()
    )
    now = datetime.now(timezone.utc)
    if row:
        row.percent = max(row.percent or 0, payload.percent)
        row.last_activity = now
    else:
        row = Progress(
            user_id=payload.user_id,
            module_id=payload.module_id,
            percent=payload.percent,
            started_at=now,
            last_activity=now,
        )
        db.add(row)
    db.commit()
    return {"ok": True, "module_id": row.module_id, "percent": row.percent}


@router.get("/stats")
def stats(user_id: int = DEFAULT_USER, db: Session = Depends(get_db)):
    total = db.query(Module).count()
    rows = db.query(Progress).filter(Progress.user_id == user_id).all()
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
def list_favorites(user_id: int = DEFAULT_USER, db: Session = Depends(get_db)):
    rows = db.query(Favorite).filter(Favorite.user_id == user_id).all()
    return [r.module_id for r in rows]


@router.post("/favorites")
def toggle_favorite(payload: FavoriteIn, db: Session = Depends(get_db)):
    if not db.get(Module, payload.module_id):
        raise HTTPException(status_code=404, detail="Módulo não encontrado")
    _ensure_user(db, payload.user_id)
    row = (
        db.query(Favorite)
        .filter(Favorite.user_id == payload.user_id, Favorite.module_id == payload.module_id)
        .first()
    )
    if row:
        db.delete(row)
        db.commit()
        return {"favorited": False, "module_id": payload.module_id}
    db.add(Favorite(user_id=payload.user_id, module_id=payload.module_id))
    db.commit()
    return {"favorited": True, "module_id": payload.module_id}
