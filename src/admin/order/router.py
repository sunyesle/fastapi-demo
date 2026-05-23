from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Depends

from src.admin.schemas import AdminOrderSchema
from src.auth.dependencies import get_current_admin_user
from src.common.pagination import Page, PaginationQuery
from src.database import get_db_read_session
from src.admin.order.service import admin_order_service
from src.enums import OrderStatus
from src.models.user import User


router = APIRouter(prefix="/admin/orders", tags=["admin-order-dashboard"])

@router.get("", response_model=Page[AdminOrderSchema])
async def order_list(
    pagination: PaginationQuery,
    status: OrderStatus | None = None,
    admin: User = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_db_read_session),
) -> Page[AdminOrderSchema]:
    results, count = await admin_order_service.get_order_list(
        session,
        status=status,
        pagination=pagination,
    )

    return Page.from_paginated_results(
        [AdminOrderSchema.model_validate(r) for r in results],
        count,
        pagination
    )
