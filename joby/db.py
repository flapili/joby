# coding: utf-8
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from .settings import get_settings


s = get_settings()
psql_url = f"postgresql+asyncpg://{s.postgres_user}:{s.postgres_password.get_secret_value()}@{s.postgres_host}:{s.postgres_port}/{s.postgres_database}"  # noqa
engine = create_async_engine(psql_url)


async def get_session() -> AsyncSession:
    async with AsyncSession(engine) as session:
        return session
