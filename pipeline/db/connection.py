"""
Database connection and session management.
Uses SQLite for simplicity — upgrade path to PostgreSQL if needed.
"""

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from pipeline.db.models import Base


# Resolve data directory relative to project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "db.sqlite"


def get_engine(db_url: str = None):
    """Create and return a SQLAlchemy engine."""
    # Ensure data directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if db_url is None:
        env_url = os.getenv("DATABASE_URL")
        if env_url and not env_url.strip().startswith("sqlite:///data"):
            db_url = env_url
        else:
            db_posix = DB_PATH.as_posix()
            db_url = f"sqlite:///{db_posix}"
    
    engine = create_engine(
        db_url,
        echo=False,
        # SQLite-specific: enable WAL mode for better concurrent access
        connect_args={"check_same_thread": False} if "sqlite" in db_url else {},
    )
    return engine


def get_session(engine=None) -> Session:
    """Create and return a new database session."""
    if engine is None:
        engine = get_engine()
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()


def init_db(engine=None):
    """Initialize the database — create all tables."""
    if engine is None:
        engine = get_engine()
    Base.metadata.create_all(engine)
    print(f"[OK] Database initialized at {DB_PATH}")
    return engine
