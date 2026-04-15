from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.image import delete_image, save_image
from src.common.pagination import Page, PaginationQuery
from src.database import get_db_read_session, get_db_session
from src.exceptions import ResourceNotFound
from src.product import service as product_service
from src.product.schemas import ProductImageSchema, ProductSchema, ProductCreate, ProductUpdate
from src.product.service import product_service
from src.models import Product, ProductImage


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

@router.put("/{id}", response_model=ProductSchema)
async def update_product(
    id: int,
    product_update: ProductUpdate,
    session: AsyncSession = Depends(get_db_session),
) -> Product:
    product = await product_service.get(session, id)

    if product is None:
        raise ResourceNotFound()
    
    return await product_service.update(session, product, product_update)

@router.delete("/{id}", status_code=204)
async def delete_product(
    id: int,
    session: AsyncSession = Depends(get_db_session),
) -> None:
    product = await product_service.get(session, id)

    if product is None:
        raise ResourceNotFound()
    
    await product_service.delete(session, product)

@router.post("/{id}/images", response_model=ProductImageSchema, status_code=201)
async def save_product_image(
    id: int,
    image: UploadFile = File(...),
    session: AsyncSession = Depends(get_db_session),
) -> ProductImage:
    product = await product_service.get(session, id)

    if product is None:
        raise ResourceNotFound()
    
    url = await save_image(image, folder="products")

    product_image = await product_service.add_image(session, product, url)

    return product_image

@router.delete("/{id}/images/{image_id}", status_code=204)
async def delete_product_image(
    id: int,
    image_id: int,
    session: AsyncSession = Depends(get_db_session),
) -> None:
    image = await product_service.get_image(session, image_id)

    if image is None or image.product_id != id:
        raise ResourceNotFound()
    
    delete_image(image.url)

    await product_service.delete_image(session, image)
