from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.pagination import Page, PaginationQuery
from src.database import get_db_read_session, get_db_session
from src.exceptions import ResourceNotFound
from src.product import service as product_service
from src.product.schemas import ProductSchema, ProductCreate
from src.product.service import product_service
from src.models.product import Product


router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=Page[ProductSchema])
async def list(
    pagination: PaginationQuery,
    category_id: int | None = None,
    active_only: bool = True,
    featured_only: bool = False,
    session: AsyncSession = Depends(get_db_read_session),
) -> Page[ProductSchema]:
    results, count = await product_service.list(
        session,
        category_id=category_id,
        active_only=active_only,
        featured_only=featured_only,
        pagination=pagination,
    )

    return Page.from_paginated_results(
        [ProductSchema.model_validate(r) for r in results],
        count,
        pagination
    )

@router.get("/{id}", response_model=ProductSchema)
async def get(
    id: int,
    session: AsyncSession = Depends(get_db_read_session),             
) -> Product:
    product = await product_service.get(session, id)
    
    if product is None:
        raise ResourceNotFound()
    
    return product

@router.post("/", response_model=ProductSchema, status_code=201)
async def create(
    product_create: ProductCreate,
    session: AsyncSession = Depends(get_db_session),
) -> Product:
    return await product_service.create(session, product_create)
