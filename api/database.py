from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os

DB_PATH = os.environ.get(
    "APRENDE_DB",
    os.path.join(os.path.dirname(__file__), "..", "data", "aprende.db"),
)
engine = create_engine(
    f"sqlite:///{DB_PATH}",
    echo=False,
    # FastAPI roda várias threads; o SQLite precisa de check_same_thread=False
    # e um timeout curto para não bloquear indefinidamente sob escrita.
    connect_args={"check_same_thread": False, "timeout": 15},
)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
