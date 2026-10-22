from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config.settings import settings

engine = create_engine(settings.database_url)  # Created once, manages the connection pool

SessionLocal = sessionmaker(bind=engine, autoflush=False)

class Base(DeclarativeBase):
    """Parent class for every table model; Alembic reads Base.metadata."""
    pass

def get_db():
    """FastAPI dependency: opens a session per request and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
