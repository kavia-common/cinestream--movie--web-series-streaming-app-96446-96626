from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from src.core.config import get_settings

settings = get_settings()
DATABASE_URL = settings.assembled_database_url()

# echo=True can be enabled for debugging
engine = create_engine(
    DATABASE_URL,
    future=True,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

Base = declarative_base()


# PUBLIC_INTERFACE
def init_db() -> None:
    """Create database tables if they do not exist."""
    from src.models import models  # noqa: F401  # ensure models are imported for metadata
    Base.metadata.create_all(bind=engine)


@contextmanager
# PUBLIC_INTERFACE
def get_db() -> Generator:
    """Provide a transactional scope around a series of operations."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
