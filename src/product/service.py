from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models import Product
from src.product.schemas import ProductCreate, ProductUpdate


def get_products(session: Session, skip: int = 0, limit: int = 100):
    statement = (
        select(Product)
        .offset(skip)
        .limit(limit)
    )

    result = session.execute(statement)
    return result.scalars().all()


def get_product(session: Session, id: int):
    statement = (
        select(Product)
        .where(Product.id == id)
    )

    result = session.execute(statement)
    return result.unique().scalar_one_or_none()


def create_product(session: Session, create_schema: ProductCreate):
    product = Product(**create_schema.model_dump())
    session.add(product)
    session.flush()
    return product


def update_product(session: Session, product: Product, update_schema: ProductUpdate):
    if update_schema.name is not None:
        product.name = update_schema.name

    if update_schema.price is not None:
        product.price = update_schema.price

    session.add(product)
    session.flush()
    return product


def delete_product(session: Session, product: Product):
    session.delete(product)
    session.flush()
    return product
