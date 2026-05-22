from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.common.pagination import Pagination
from src.enums import OrderStatus
from src.models.order import Order


class AdminOrderService():

    async def get_order_list(
        self,
        session: AsyncSession,
        pagination: Pagination,
        status: OrderStatus | None = None,
    ) -> tuple[Sequence[Order], int]:
        statement = (
            select(Order)
            .options(selectinload(Order.items))
        )

        if status is not None:
            statement = statement.where(Order.status == status)

        count_statement = select(func.count()).select_from(statement.subquery())
        count_result = await session.execute(count_statement)
        count = count_result.scalar_one()

        offset = (pagination.page - 1) * pagination.size
        statement = statement.offset(offset).limit(pagination.size)
        result = await session.execute(statement)
        results = result.scalars().all()

        return results, count


admin_order_service = AdminOrderService()
