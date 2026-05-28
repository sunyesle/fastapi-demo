from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.pagination import Pagination
from src.exceptions import ResourceNotFound
from src.models import User


class AdminUserService():

    async def get_user_list(
        self,
        session: AsyncSession,
        pagination: Pagination,
        search: str | None = None,
    ) -> tuple[Sequence[User], int]:
        statement = select(User)

        if search is not None:
            statement = statement.where(User.name.like(f"%{search}%"))

        count_statement = select(func.count()).select_from(statement.subquery())
        count_result = await session.execute(count_statement)
        count = count_result.scalar_one()

        offset = (pagination.page - 1) * pagination.size
        statement = statement.offset(offset).limit(pagination.size)
        result = await session.execute(statement)
        results = result.scalars().all()

        return results, count

    async def get_user(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> User:
        statement = (
            select(User)
            .where(User.id == user_id)
        )
        result = await session.execute(statement)
        user = result.scalar_one_or_none()

        if user is None:
            raise ResourceNotFound()

        return user


admin_user_service = AdminUserService()
