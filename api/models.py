from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Track(Base):
    __tablename__ = "tracks"
    id = Column(String(32), primary_key=True)
    label = Column(String(64), nullable=False)
    eyebrow = Column(String(128))
    description = Column(Text)
    color = Column(String(32))
    icon = Column(String(32))
    target_modules = Column(Integer, default=0)
    modules = relationship("Module", back_populates="track_rel")


class Module(Base):
    __tablename__ = "modules"
    id = Column(String(64), primary_key=True)
    track_id = Column(String(32), ForeignKey("tracks.id"), nullable=False)
    title = Column(String(256), nullable=False)
    subtitle = Column(Text)
    level = Column(String(64))
    level_order = Column(Integer, default=0)
    duration_min = Column(Integer, default=10)
    age_group = Column(String(64))
    objectives = Column(Text)
    content_json = Column(Text)
    featured = Column(Boolean, default=False)
    accent = Column(String(32), default="blue")
    icon = Column(String(32), default="BookOpen")
    created_at = Column(DateTime, default=_utcnow)
    track_rel = relationship("Track", back_populates="modules")
    steps = relationship(
        "ModuleStep", back_populates="module_rel", order_by="ModuleStep.order"
    )


class ModuleStep(Base):
    __tablename__ = "module_steps"
    id = Column(Integer, primary_key=True, autoincrement=True)
    module_id = Column(String(64), ForeignKey("modules.id"), nullable=False)
    order = Column(Integer, nullable=False)
    step_type = Column(String(32), nullable=False)  # explanation, example, practice, check, next
    title = Column(String(256))
    # Contrato StepData.content: {"text": str, "objectives"?: [...], "activities"?: [...]}
    content_json = Column(Text, nullable=False)
    module_rel = relationship("Module", back_populates="steps")

    __table_args__ = (UniqueConstraint("module_id", "order", name="uq_step_module_order"),)


class User(Base):
    """Conta mínima.

    O campus anônimo não preenche nome nem e-mail. Os campos existem para um
    eventual uso institucional, mas nenhuma rota pública os coleta.
    """

    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128))
    email = Column(String(320), unique=True)
    role = Column(String(16), default="student")
    created_at = Column(DateTime, default=_utcnow)


class UserSession(Base):
    """Sessão autenticada por token opaco (só o hash SHA-256 é persistido)."""

    __tablename__ = "user_sessions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    token_hash = Column(String(64), nullable=False, unique=True, index=True)
    created_at = Column(DateTime, default=_utcnow)
    last_seen_at = Column(DateTime, default=_utcnow)
    expires_at = Column(DateTime, nullable=False)
    revoked_at = Column(DateTime)


class Progress(Base):
    __tablename__ = "progress"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    module_id = Column(String(64), ForeignKey("modules.id"), nullable=False)
    percent = Column(Float, default=0)
    # Etapas concluídas (JSON com lista de ordens). Mantém compatibilidade com
    # o modo local, que já guarda a granularidade por etapa.
    completed_json = Column(Text)
    started_at = Column(DateTime, default=_utcnow)
    last_activity = Column(DateTime, default=_utcnow)

    __table_args__ = (
        UniqueConstraint("user_id", "module_id", name="uq_progress_user_module"),
    )


class Favorite(Base):
    __tablename__ = "favorites"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    module_id = Column(String(64), ForeignKey("modules.id"), nullable=False)
    created_at = Column(DateTime, default=_utcnow)

    __table_args__ = (
        UniqueConstraint("user_id", "module_id", name="uq_favorite_user_module"),
    )
