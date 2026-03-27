from __future__ import annotations

from functools import lru_cache

from .config import (
    DATABASE_URL,
    POSTGRES_DB,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_USER,
)


def _build_sqlalchemy_url() -> str:
    if DATABASE_URL and DATABASE_URL.strip():
        return DATABASE_URL

    return (
        f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
        f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )


@lru_cache(maxsize=1)
def get_engine():
    """Create (and cache) a SQLAlchemy engine for Postgres.

    Environment variables:
      - DATABASE_URL (optional)
      - POSTGRES_HOST (default: localhost)
      - POSTGRES_PORT (default: 5432)
      - POSTGRES_DB (default: plagiarism)
      - POSTGRES_USER (default: plagiarism)
      - POSTGRES_PASSWORD (default: plagiarism)
    """

    try:
        from sqlalchemy import create_engine  # type: ignore
    except ImportError as e:  # pragma: no cover
        raise ImportError(
            "Missing dependency 'sqlalchemy'. Install it in your venv, e.g. 'pip install sqlalchemy'."
        ) from e

    url = _build_sqlalchemy_url()
    return create_engine(url, pool_pre_ping=True)


def get_session_maker():
    """Return a configured SQLAlchemy sessionmaker bound to the engine."""

    try:
        from sqlalchemy.orm import sessionmaker  # type: ignore
    except ImportError as e:  # pragma: no cover
        raise ImportError(
            "Missing dependency 'sqlalchemy'. Install it in your venv, e.g. 'pip install sqlalchemy'."
        ) from e

    engine = get_engine()
    return sessionmaker(bind=engine, autocommit=False, autoflush=False)
