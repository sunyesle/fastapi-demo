from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models import Product
from src.product.schemas import ProductCreate, ProductUpdate


def get_products(db: Session, skip: int = 0, limit: int = 100):
    statement = (
        select(Product)
        .where(Product.deleted_at.is_(None))
        .offset(skip)
        .limit(limit)
    )

    result = db.execute(statement)
    return result.scalars().all()


def get_product(db: Session, id: int):
    statement = (
        select(Product)
        .where(
            Product.id == id,
            Product.deleted_at.is_(None)
        )
    )

    result = db.execute(statement)
    return result.unique().scalar_one_or_none()


def create_product(db: Session, create_schema: ProductCreate):
    product = Product(**create_schema.model_dump())
    db.add(product)
    db.flush()
    return product


def update_product(db: Session, product: Product, update_schema: ProductUpdate):
    if update_schema.name is not None:
        product.name = update_schema.name

    if update_schema.price is not None:
        product.price = update_schema.price

    db.add(product)
    db.flush()
    return product


def delete_product(db: Session, product: Product):
    product.set_deleted_at()
    db.flush()
    return product
