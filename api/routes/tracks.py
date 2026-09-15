from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from ..models import Track, Module

router = APIRouter(prefix="/api/tracks", tags=["tracks"])


@router.get("")
def list_tracks(db: Session = Depends(get_db)):
    tracks = db.query(Track).all()
    result = []
    for t in tracks:
        count = db.query(func.count(Module.id)).filter(Module.track_id == t.id).scalar()
        result.append({
            "id": t.id,
            "label": t.label,
            "eyebrow": t.eyebrow,
            "description": t.description,
            "color": t.color,
            "icon": t.icon,
            "target_modules": t.target_modules,
            "module_count": count,
        })
    return result
