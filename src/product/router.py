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

@router.get("/{product_id}", response_model=ProductSchema)
async def get(
    product_id: int,
    session: AsyncSession = Depends(get_db_read_session),
) -> Product:
    product = await product_service.get(session, product_id)

    if product is None:
        raise ResourceNotFound()

    return product

@router.post("/", response_model=ProductSchema, status_code=201)
async def create(
    product_create: ProductCreate,
    session: AsyncSession = Depends(get_db_session),
) -> Product:
    return await product_service.create(session, product_create)

@router.put("/{product_id}", response_model=ProductSchema)
async def update_product(
    product_id: int,
    product_update: ProductUpdate,
    session: AsyncSession = Depends(get_db_session),
) -> Product:
    return await product_service.update(session, product_id, product_update)

@router.delete("/{product_id}", status_code=204)
async def delete_product(
    product_id: int,
    session: AsyncSession = Depends(get_db_session),
) -> None:
    await product_service.delete(session, product_id)

@router.post("/{product_id}/images", response_model=ProductImageSchema, status_code=201)
async def save_product_image(
    product_id: int,
    image: UploadFile = File(...),
    session: AsyncSession = Depends(get_db_session),
) -> ProductImage:
    product = await product_service.get(session, product_id)

    url = await save_image(image, folder="products")

    product_image = await product_service.add_image(session, product_id, len(product.images), url)

    return product_image

@router.delete("/{product_id}/images/{image_id}", status_code=204)
async def delete_product_image(
    product_id: int,
    image_id: int,
    session: AsyncSession = Depends(get_db_session),
) -> None:
    image = await product_service.get_image(session, product_id, image_id)

    delete_image(image.url)

    await product_service.delete_image(session, product_id, image_id)
