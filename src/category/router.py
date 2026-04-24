from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.category.schemas import CategoryCreate, CategorySchema, CategoryUpdate
from src.category.service import category_service
from src.common.pagination import Page, PaginationQuery
from src.database import get_db_read_session, get_db_session
from src.exceptions import ResourceNotFound
from src.models import Category


router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=Page[CategorySchema])
async def list(
    pagination: PaginationQuery,
    active_only: bool = True,
    session: AsyncSession = Depends(get_db_read_session),
) -> Page[CategorySchema]:
    results, count = await category_service.list(session, active_only, pagination)

    return Page.from_paginated_results(
        [CategorySchema.model_validate(r) for r in results],
        count,
        pagination
    )

@router.get("/{id}", response_model=CategorySchema)
async def get(
    id: int,
    session: AsyncSession = Depends(get_db_read_session),
) -> Category:
    category = await category_service.get(session, id)

    if category is None:
        raise ResourceNotFound()

    return category

@router.post("/", response_model=CategorySchema, status_code=201)
async def create(
    category_create: CategoryCreate,
    session: AsyncSession = Depends(get_db_session),
) -> Category:
    return await category_service.create(session, category_create)

@router.put("/{id}", response_model=CategorySchema)
async def update(
    id: int,
    category_update: CategoryUpdate,
    session: AsyncSession = Depends(get_db_session),
) -> Category:
    category = await category_service.get(session, id)

    if category is None:
        raise ResourceNotFound()

    await category_service.update(session, category, category_update)

    return category

@router.delete("/{id}", status_code=204)
async def delete(
    id: int,
    session: AsyncSession = Depends(get_db_session),
) -> None:
    category = await category_service.get(session, id)

    if category is None:
        raise ResourceNotFound()

    await category_service.delete(session, category)
