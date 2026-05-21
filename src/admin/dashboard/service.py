from datetime import datetime, timedelta
from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.admin.schemas import AdminOrderSchema
from src.common.utils import utc_now
from src.enums import OrderStatus
from src.models import Order, Product, User


class DashboardService():

    async def get_dashboard_stats(
        self,
        session: AsyncSession,
    ) -> dict:
        today = utc_now()
        start_of_month = today.replace(day=1)

        return {
            "orders": await self.get_order_stats(session, today, start_of_month),
            "revenue": await self.get_revenue_stats(session, today, start_of_month),
            "users": await self.get_user_stats(session, today, start_of_month),
            "products": await self.get_product_stats(session, today, start_of_month),
        }

    async def get_order_stats(
        self,
        session: AsyncSession,
        today: datetime,
        start_of_month: datetime,
    ) -> dict:
        # 오늘 주문
        today_orders = (await session.execute(
            select(func.count(Order.id)).where(
                func.date(Order.created_at) == today,
            )
        )).scalar_one()

        # 이번 달 주문
        month_orders = (await session.execute(
            select(func.count(Order.id)).where(
                func.date(Order.created_at) >= start_of_month,
            )
        )).scalar_one()

        # 처리 대기 주문
        pending_orders = (await session.execute(
            select(func.count(Order.id)).where(
                Order.status.in_([OrderStatus.paid, OrderStatus.preparing]),
            )
        )).scalar_one()

        return {
            "today": today_orders,
            "month": month_orders,
            "pending": pending_orders,
        }

    async def get_revenue_stats(
        self,
        session: AsyncSession,
        today: datetime,
        start_of_month: datetime,
    ) -> dict:
        # 오늘 매출
        today_revenue = (await session.execute(
            select(func.coalesce(func.sum(Order.final_price), 0)).where(
                func.date(Order.paid_at) == today,
                Order.status != OrderStatus.cancelled,
            )
        )).scalar_one()

        # 이번 달 매출
        month_revenue = (await session.execute(
            select(func.coalesce(func.sum(Order.final_price), 0)).where(
                func.date(Order.paid_at) == today,
                Order.status != OrderStatus.cancelled,
            )
        )).scalar_one()

        return {
            "today": today_revenue,
            "month": month_revenue,
        }

    async def get_user_stats(
        self,
        session: AsyncSession,
        today: datetime,
        start_of_month: datetime,
    ) -> dict:
        # 전체 회원
        total_users = (await session.execute(
            select(func.count(User.id))
        )).scalar_one()

        # 오늘 가입
        today_users = (await session.execute(
            select(func.count(User.id)).where(
                func.date(User.created_at) == today,
            )
        )).scalar_one()

        return {
            "total": total_users,
            "today": today_users,
        }

    async def get_product_stats(
        self,
        session: AsyncSession,
        today: datetime,
        start_of_month: datetime,
    ) -> dict:
        # 전체 상품
        total_products = (await session.execute(
            select(func.count(Product.id))
        )).scalar_one()

        # 재고 부족 (10개 미만)
        low_stock = (await session.execute(
            select(func.count(Product.id)).where(
                Product.stock < 10,
                Product.is_active == True,
            )
        )).scalar_one()

        return {
            "total": total_products,
            "low_stock": low_stock,
        }

    async def get_recent_orders(
        self,
        session: AsyncSession,
        limit: int = 10,
    ) ->  Sequence[AdminOrderSchema]:
        # 최근 주문
        recent_orders = (await session.execute(
            select(Order)
            .options(selectinload(Order.items))
            .order_by(Order.created_at.desc())
            .limit(limit)
        )).scalars().all()

        return [AdminOrderSchema.model_validate(r) for r in recent_orders]
    
    async def get_sales_chart_data(
        self,
        session: AsyncSession,
        days: int = 7,
    ) -> dict:
        # 일별 매출
        today = utc_now()
        labels = []
        data = []

        for i in range(days - 1, -1, -1):
            date = today - timedelta(days=i)
            labels.append(date.strftime("%m/%d"))

            revenue = (await session.execute(
                select(func.coalesce(func.sum(Order.final_price), 0)).where(
                    func.date(Order.paid_at) == date,
                    Order.status != OrderStatus.cancelled,
                )
            )).scalar_one()
            data.append(revenue)

        return {"labels": labels, "data": data}


dashboard_service = DashboardService()
