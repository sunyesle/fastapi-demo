from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models import Item
from src.item.schemas import ItemCreate, ItemUpdate


def get_items(db: Session, skip: int = 0, limit: int = 100):
    statement = select(Item).offset(skip).limit(limit)

    result = db.execute(statement)
    return result.scalars().all()


def get_item(db: Session, id: int):
    statement = select(Item).where(Item.id == id)

    result = db.execute(statement)
    return result.unique().scalar_one_or_none()


def create_item(db: Session, create_schema: ItemCreate):
    item = Item(**create_schema.model_dump())
    db.add(item)
    db.flush()
    return item


def update_item(db: Session, item: Item, update_schema: ItemUpdate):
    if update_schema.name is not None:
        item.name = update_schema.name

    if update_schema.price is not None:
        item.price = update_schema.price

    db.add(item)
    db.flush()
    return item


def delete_item(db: Session, item: Item):
    db.delete(item)
    db.flush()
    return item
