from typing import List

from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from database import engine, SessionLocal
from models import Model
from schemas import Item, ItemCreate
import service

app = FastAPI()

Model.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/items/")
def get_items(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> List[Item]:
    return service.get_items(db, skip=skip, limit=limit)


@app.post("/items/")
def create_item(
    item_create: ItemCreate,
    db: Session = Depends(get_db),
) -> Item:
    return service.create_item(db, item_create=item_create)
