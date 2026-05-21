"""Database setup — async SQLAlchemy med session-dependency til FastAPI."""

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    pass


engine = create_async_engine(settings.database_url, echo=False, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session


async def init_db() -> None:
    """Opret tabeller hvis de mangler + kør lette idempotente migrationer.

    Vi bruger Postgres' ADD COLUMN IF NOT EXISTS for at undgå at miste data
    når vi tilføjer felter. Når skemaet bliver komplekst skifter vi til Alembic.
    """
    from sqlalchemy import text

    from app import models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        # Idempotente migrationer (PostgreSQL ADD COLUMN IF NOT EXISTS)
        migrations = [
            "ALTER TABLE tenants ADD COLUMN IF NOT EXISTS relationship_type VARCHAR(20) NOT NULL DEFAULT 'sponsor'",
            "ALTER TABLE tenants ADD COLUMN IF NOT EXISTS own_brand_name VARCHAR(200)",
            "ALTER TABLE tenants ADD COLUMN IF NOT EXISTS own_brand_search_text VARCHAR(500)",
            "ALTER TABLE tracked_entities ADD COLUMN IF NOT EXISTS last_ave_dkk BIGINT NOT NULL DEFAULT 0",
        ]
        for sql in migrations:
            await conn.execute(text(sql))
