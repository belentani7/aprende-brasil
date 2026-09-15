from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .database import Base


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
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    track_rel = relationship("Track", back_populates="modules")
    steps = relationship("ModuleStep", back_populates="module_rel", order_by="ModuleStep.order")


class ModuleStep(Base):
    __tablename__ = "module_steps"
    id = Column(Integer, primary_key=True, autoincrement=True)
    module_id = Column(String(64), ForeignKey("modules.id"), nullable=False)
    order = Column(Integer, nullable=False)
    step_type = Column(String(32), nullable=False)  # explanation, example, practice, check, next
    title = Column(String(256))
    content_json = Column(Text, nullable=False)
    module_rel = relationship("Module", back_populates="steps")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128))
    email = Column(String(320))
    role = Column(String(16), default="student")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Progress(Base):
    __tablename__ = "progress"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    module_id = Column(String(64), ForeignKey("modules.id"), nullable=False)
    percent = Column(Float, default=0)
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_activity = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Favorite(Base):
    __tablename__ = "favorites"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    module_id = Column(String(64), ForeignKey("modules.id"), nullable=False)
