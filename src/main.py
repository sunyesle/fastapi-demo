import contextlib
from typing import AsyncIterator, TypedDict

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

from src.common.models import Model
from src.database import create_engine, create_sessionmaker, get_db_read_session, get_db_session
from src.models import Item
from src.schemas import Item as ItemSchema
from src.schemas import ItemCreate, ItemUpdate
import src.service as service


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
    
    return app


app = create_app()


@app.get("/items/", response_model=list[ItemSchema])
def get_items(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db_read_session),
) -> list[Item]:
    return service.get_items(db, skip=skip, limit=limit)


@app.get("/items/{id}", response_model=ItemSchema)
def get_item(
    id: int,
    db: Session = Depends(get_db_read_session),             
) -> Item:
    item = service.get_item(db, id)
    
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return item


@app.post("/items/", response_model=ItemSchema)
def create_item(
    item_create: ItemCreate,
    db: Session = Depends(get_db_session),
) -> Item:
    return service.create_item(db, item_create)


@app.put("/items/{id}", response_model=ItemSchema)
def update_item(
    id: int,
    item_update: ItemUpdate,
    db: Session = Depends(get_db_session),
) -> Item:
    item = service.get_item(db, id)

    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return service.update_item(db, item, item_update)


@app.delete("/items/{id}", status_code=204)
def delete_item(
    id: int,
    db: Session = Depends(get_db_session),
):
    item = service.get_item(db, id)

    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    service.delete_item(db, item)
    
    return None
