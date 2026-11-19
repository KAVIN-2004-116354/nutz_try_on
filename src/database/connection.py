import os
from pathlib import Path
from typing import Generator
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session

# Locate and load environment variables from project root .env
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://nutz_admin:nutz_admin_password_2026@127.0.0.1:5432/nutz_try_on"
)

# Robust PostgreSQL Connection Pool Settings
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=300,
    pool_pre_ping=True,
    echo=False
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency yielding a thread-safe database session with
    automatic rollback on unhandled exceptions and guaranteed cleanup.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
