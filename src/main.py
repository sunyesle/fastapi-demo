from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from src.common.models import Model
from src.database import engine, SessionLocal
from src.models import Item
from src.schemas import Item as ItemSchema
from src.schemas import ItemCreate, ItemUpdate
import src.service as service

app = FastAPI()

Model.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/items/", response_model=list[ItemSchema])
def get_items(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> list[Item]:
    return service.get_items(db, skip=skip, limit=limit)


@app.get("/items/{id}", response_model=ItemSchema)
def get_item(
    id: int,
    db: Session = Depends(get_db),             
) -> Item:
    item = service.get_item(db, id)
    
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return item


@app.post("/items/", response_model=ItemSchema)
def create_item(
    item_create: ItemCreate,
    db: Session = Depends(get_db),
) -> Item:
    return service.create_item(db, item_create)


@app.put("/items/{id}", response_model=ItemSchema)
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
