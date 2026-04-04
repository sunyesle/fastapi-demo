from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db_read_session, get_db_session
from src.item import service as item_service
from src.item.schemas import Item as ItemSchema, ItemCreate, ItemUpdate
from src.models.item import Item

router = APIRouter(prefix="/items", tags=["items"])

@router.get("/", response_model=list[ItemSchema])
def get_items(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db_read_session),
) -> list[Item]:
    return item_service.get_items(db, skip=skip, limit=limit)


@router.get("/{id}", response_model=ItemSchema)
def get_item(
    id: int,
    db: Session = Depends(get_db_read_session),             
) -> Item:
    item = item_service.get_item(db, id)
    
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return item


@router.post("/", response_model=ItemSchema)
def create_item(
    item_create: ItemCreate,
    db: Session = Depends(get_db_session),
) -> Item:
    return item_service.create_item(db, item_create)


@router.put("/{id}", response_model=ItemSchema)
def update_item(
    id: int,
    item_update: ItemUpdate,
    db: Session = Depends(get_db_session),
) -> Item:
    item = item_service.get_item(db, id)

    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return item_service.update_item(db, item, item_update)


@router.delete("/{id}", status_code=204)
def delete_item(
    id: int,
    db: Session = Depends(get_db_session),
):
    item = item_service.get_item(db, id)

    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    item_service.delete_item(db, item)
    
    return None
