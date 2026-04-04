import contextlib
from typing import AsyncIterator, TypedDict

from fastapi import FastAPI
from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

from src.common.models import Model
from src.api import router
from src.database import create_engine, create_sessionmaker
from src.exeption_handlers import add_exception_handlers


class State(TypedDict):
    engine: Engine
    sessionmaker: sessionmaker[Session]


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[State]:
    # [STARTUP] 서버가 켜질 때 실행될 로직
    engine = create_engine()
    sessionmaker = create_sessionmaker(engine)

    Model.metadata.create_all(bind=engine)

    yield{
        "engine": engine,
        "sessionmaker": sessionmaker
    }

    # [SHUTDOWN] 서버가 꺼질 때 실행될 로직
    engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        lifespan=lifespan
    )

    add_exception_handlers(app)

    app.include_router(router)

    return app


app = create_app()
