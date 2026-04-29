from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user
from src.common.pagination import Page, PaginationQuery
from src.user.schemas import UserCreate, UserSchema, UserUpdate
from src.user.service import user_service
from src.database import get_db_read_session, get_db_session
from src.models import User


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserSchema)
async def me(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_read_session),
) -> User:
    return await user_service.get(session, user.id)

@router.get("/", response_model=Page[UserSchema])
async def list(
    pagination: PaginationQuery,
    active_only: bool = True,
    session: AsyncSession = Depends(get_db_read_session),
) -> Page[UserSchema]:
    results, count = await user_service.list(session, active_only, pagination)

    return Page.from_paginated_results(
        [UserSchema.model_validate(r) for r in results],
        count,
        pagination
    )

@router.get("/{user_id}", response_model=UserSchema)
async def get(
    user_id: int,
    session: AsyncSession = Depends(get_db_read_session),
) -> User:
    user = await user_service.get(session, user_id)

    return user

@router.post("/", response_model=UserSchema, status_code=201)
async def create(
    user_create: UserCreate,
    session: AsyncSession = Depends(get_db_session),
) -> User:
    return await user_service.create(session, user_create)

@router.put("/{user_id}", response_model=UserSchema)
async def update(
    user_id: int,
    user_update: UserUpdate,
    session: AsyncSession = Depends(get_db_session),
) -> User:
    return await user_service.update(session, user_id, user_update)

@router.delete("/{user_id}", status_code=204)
async def delete(
    user_id: int,
    session: AsyncSession = Depends(get_db_session),
) -> None:
    await user_service.delete(session, user_id)
