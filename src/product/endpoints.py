from typing import Sequence

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.database import get_db_read_session, get_db_session
from src.exceptions import ResourceNotFound
from src.product import service as product_service
from src.product.schemas import Product as ProductSchema, ProductCreate, ProductUpdate
from src.models.product import Product


router = APIRouter(prefix="/products", tags=["products"])

@router.get("/", response_model=list[ProductSchema])
def get_products(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db_read_session),
) -> Sequence[Product]:
    return product_service.get_products(db, skip=skip, limit=limit)


@router.get("/{id}", response_model=ProductSchema)
def get_product(
    id: int,
    db: Session = Depends(get_db_read_session),             
) -> Product:
    product = product_service.get_product(db, id)
    
    if product is None:
        raise ResourceNotFound()
    
    return product


@router.post("/", response_model=ProductSchema, status_code=201)
def create_product(
    product_create: ProductCreate,
    db: Session = Depends(get_db_session),
) -> Product:
    return product_service.create_product(db, product_create)


@router.put("/{id}", response_model=ProductSchema)
def update_product(
    id: int,
    product_update: ProductUpdate,
    db: Session = Depends(get_db_session),
) -> Product:
    product = product_service.get_product(db, id)

    if product is None:
        raise ResourceNotFound()
    
    return product_service.update_product(db, product, product_update)


@router.delete("/{id}", status_code=204)
def delete_product(
    id: int,
    db: Session = Depends(get_db_session),
):
    product = product_service.get_product(db, id)

    if product is None:
        raise ResourceNotFound()
    
    product_service.delete_product(db, product)
    
    return None
