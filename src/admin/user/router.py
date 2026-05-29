from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Depends

from src.admin.schemas import AdminUserSchema, AdminUserStatusUpdate
from src.admin.user.service import admin_user_service
from src.auth.dependencies import get_current_admin_user
from src.common.pagination import Page, PaginationQuery
from src.database import get_db_read_session, get_db_session
from src.models.user import User

router = APIRouter(prefix="/admin/users", tags=["admin-user-dashboard"])

@router.get("", response_model=Page[AdminUserSchema])
async def user_list(
    pagination: PaginationQuery,
    search: str | None = None,
    admin: User = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_db_read_session),
) -> Page[AdminUserSchema]:
    results, count = await admin_user_service.get_user_list(
        session,
        search=search,
        pagination=pagination,
    )

    return Page.from_paginated_results(
        [AdminUserSchema.model_validate(r) for r in results],
        count,
        pagination
    )

@router.get("/{user_id}", response_model=AdminUserSchema)
async def user_detail(
    user_id: int,
    admin: User = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_db_read_session),
) -> User:
    return await admin_user_service.get_user(session, user_id)

@router.put("/{user_id}/status", response_model=AdminUserSchema)
async def update_user_status(
    user_id: int,
    user_update: AdminUserStatusUpdate,
    admin: User = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_db_session),
) -> User:
    return await admin_user_service.update_user_status(session, user_id, user_update)
