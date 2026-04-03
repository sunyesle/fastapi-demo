from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from src.database import engine, SessionLocal
from src.models import Model
from src.schemas import Item, ItemCreate, ItemUpdate
import src.service as service

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


@app.get("/items/{id}")
def get_item(
    id: int,
    db: Session = Depends(get_db),             
) -> Item:
    item = service.get_item(db, id)
    
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return item


@app.post("/items/")
def create_item(
    item_create: ItemCreate,
    db: Session = Depends(get_db),
) -> Item:
    return service.create_item(db, item_create)


@app.put("/items/{id}")
def update_item(
    id: int,
    item_update: ItemUpdate,
    db: Session = Depends(get_db),
) -> Item:
    item = service.get_item(db, id)

    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return service.update_item(db, item, item_update)


@app.delete("/items/{id}", status_code=204)
def delete_item(
    id: int,
    db: Session = Depends(get_db),
):
    item = service.get_item(db, id)

    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    service.delete_item(db, item)
    
    return None
