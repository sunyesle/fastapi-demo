from sqlalchemy.orm import Session

from models import Item
from schemas import ItemCreate


def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Item).offset(skip).limit(limit).all()

def create_item(db: Session, item_create: ItemCreate):
    item = Item(**item_create.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
