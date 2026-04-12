import contextlib
from typing import AsyncIterator, TypedDict

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine as _create_async_engine

from src.api import router
from src.config import settings
from src.database import create_engine, create_sessionmaker, init_db
from src.exeption_handlers import add_exception_handlers


class State(TypedDict):
    engine: AsyncEngine
    sessionmaker: async_sessionmaker[AsyncSession]


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[State]:
    # [STARTUP] 서버가 켜질 때 실행될 로직
    engine = create_engine()
    sessionmaker = create_sessionmaker(engine)

    await init_db(engine)

    yield{
        "engine": engine,
        "sessionmaker": sessionmaker
    }

    # [SHUTDOWN] 서버가 꺼질 때 실행될 로직
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        lifespan=lifespan
    )

    add_exception_handlers(app)

    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

    app.include_router(router)

    return app


app = create_app()
