from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config.settings import settings

# Created once, manages the connection pool.
# Neon suspends idle computes and closes their connections, so test each one before use
# (pool_pre_ping) and replace connections older than 5 minutes (pool_recycle).
engine = create_engine(settings.database_url, pool_pre_ping=True, pool_recycle=300)

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
