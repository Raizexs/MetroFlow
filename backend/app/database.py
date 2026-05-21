"""Conexión async a PostgreSQL; si falla, el API sigue con store en RAM."""

from __future__ import annotations

import logging
import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

logger = logging.getLogger(__name__)

def _normalize_database_url(url: str) -> str:
    """Render entrega postgres://; SQLAlchemy async requiere postgresql+asyncpg://."""
    if url.startswith("postgres://"):
        return "postgresql+asyncpg://" + url[len("postgres://") :]
    if url.startswith("postgresql://") and "+asyncpg" not in url:
        return "postgresql+asyncpg://" + url[len("postgresql://") :]
    return url


DATABASE_URL = _normalize_database_url(
    os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://ocupacion:ocupacion@localhost:5432/ocupacion",
    )
)

engine = None
async_session_factory = None
db_enabled = False


class Base(DeclarativeBase):
    pass


def init_db() -> None:
    global engine, async_session_factory
    engine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
    async_session_factory = async_sessionmaker(engine, expire_on_commit=False)


async def setup_tables() -> bool:
    global db_enabled
    if engine is None:
        return False
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        db_enabled = True
        logger.info("PostgreSQL conectado y tabla ocupacion lista")
        return True
    except Exception as exc:
        db_enabled = False
        logger.warning("PostgreSQL no disponible, usando solo RAM: %s", exc)
        return False


async def dispose_db() -> None:
    if engine:
        await engine.dispose()
