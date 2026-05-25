from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.common.pagination import Pagination
from src.enums import OrderStatus
from src.exceptions import ResourceNotFound
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

    async def get_order(
        self,
        session: AsyncSession,
        order_id: int,
    ) -> Order:
        statement = (
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.id == order_id)
        )
        result = await session.execute(statement)
        order = result.scalar_one_or_none()

        if order is None:
            raise ResourceNotFound()

        return order

    async def get_order_status_counts(
        self,
        session: AsyncSession,
    ) -> dict:
        return {
            "all": await self.count_orders(session),
            "pending": await self.count_orders(session, OrderStatus.pending),
            "paid": await self.count_orders(session, OrderStatus.paid),
            "preparing": await self.count_orders(session, OrderStatus.preparing),
            "shipping": await self.count_orders(session, OrderStatus.shipping),
            "delivered": await self.count_orders(session, OrderStatus.delivered),
            "cancelled": await self.count_orders(session, OrderStatus.cancelled),
        }

    async def count_orders(
        self,
        session: AsyncSession,
        status: OrderStatus | None = None,
    ) -> int:
        statement = select(func.count(Order.id))

        if status is not None:
            statement = statement.where(Order.status == status)

        return (await session.execute(statement)).scalar_one()


admin_order_service = AdminOrderService()
