from collections.abc import Generator
from typing import AsyncGenerator

from fastapi import Request
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine as _create_async_engine

from src.common.models import Model
from src.config import settings


def create_engine() -> AsyncEngine:
    return _create_async_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=True,
    )

def create_sessionmaker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
        class_=AsyncSession
    )


async def init_db(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)


async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession]:
    # lifespan에서 저장한 sessionmaker를 사용
    sessionmaker = request.state.sessionmaker
    
    async with sessionmaker() as session:
        try:
            yield session
        except:
            await session.rollback()
            raise
        else:
            await session.commit()

async def get_db_read_session(request: Request) -> AsyncGenerator[AsyncSession]:
    # lifespan에서 저장한 sessionmaker를 사용
    sessionmaker = request.state.sessionmaker

    async with sessionmaker() as session:
        yield session
