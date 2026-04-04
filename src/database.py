from collections.abc import Generator

from fastapi import Request
from sqlalchemy import Engine, create_engine as _create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

DATABASE_URL = "sqlite:///:memory:"

def create_engine() -> Engine:
    return _create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=True,
    )

def create_sessionmaker(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
        class_=Session
    )


def get_db_session(request: Request) -> Generator[Session, None, None]:
    # lifespan에서 저장한 sessionmaker를 사용
    sessionmaker = request.state.sessionmaker
    
    session: Session = sessionmaker()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def get_db_read_session(request: Request) -> Generator[Session, None, None]:
    # lifespan에서 저장한 sessionmaker를 사용
    sessionmaker = request.state.sessionmaker

    session: Session = sessionmaker()
    try:
        yield session
    finally:
        session.close()
