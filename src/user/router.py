from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.pagination import Page, PaginationQuery
from src.user.schemas import UserCreate, UserSchema
from src.user.service import user_service
from src.database import get_db_read_session, get_db_session
from src.models.user import User


router = APIRouter(prefix="/users", tags=["users"])


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

@router.post("/", response_model=UserSchema, status_code=201)
async def create(
    user_create: UserCreate,
    session: AsyncSession = Depends(get_db_session),
) -> User:
    return await user_service.create(session, user_create)
