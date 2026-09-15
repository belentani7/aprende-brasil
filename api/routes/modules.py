from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from ..database import get_db
from ..models import Module, ModuleStep
import json

router = APIRouter(prefix="/api/modules", tags=["modules"])


@router.get("")
def list_modules(
    track: str | None = None,
    search: str | None = None,
    level: str | None = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    q = db.query(Module)
    if track:
        q = q.filter(Module.track_id == track)
    if search:
        term = f"%{search}%"
        q = q.filter((Module.title.ilike(term)) | (Module.subtitle.ilike(term)))
    if level:
        q = q.filter(Module.level == level)
    total = q.count()
    modules = q.order_by(Module.level_order, Module.title).offset((page - 1) * per_page).limit(per_page).all()
    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "items": [_serialize_module(m) for m in modules],
    }


@router.get("/featured")
def featured_modules(db: Session = Depends(get_db)):
    modules = db.query(Module).filter(Module.featured == True).limit(6).all()
    return [_serialize_module(m) for m in modules]


@router.get("/{module_id}")
def get_module(module_id: str, db: Session = Depends(get_db)):
    m = db.query(Module).options(joinedload(Module.steps)).filter(Module.id == module_id).first()
    if not m:
        return {"error": "Módulo não encontrado"}, 404
    data = _serialize_module(m)
    data["steps"] = [
        {
            "order": s.order,
            "type": s.step_type,
            "title": s.title,
            "content": json.loads(s.content_json) if s.content_json else None,
        }
        for s in m.steps
    ]
    return data


def _serialize_module(m: Module) -> dict:
    return {
        "id": m.id,
        "track_id": m.track_id,
        "title": m.title,
        "subtitle": m.subtitle,
        "level": m.level,
        "level_order": m.level_order,
        "duration_min": m.duration_min,
        "age_group": m.age_group,
        "objectives": m.objectives,
        "featured": m.featured,
        "accent": m.accent,
        "icon": m.icon,
    }
