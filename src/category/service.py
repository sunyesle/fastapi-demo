from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.category.schemas import CategoryCreate
from src.common.pagination import Pagination
from src.exceptions import CustomRequestValidationError
from src.models.category import Category


class CategoryService:

    async def list(
        self,
        session: AsyncSession,
        active_only: bool,
        pagination: Pagination,
    ) -> tuple[Sequence[Category], int]:
        statement = select(Category)

        if active_only:
            statement = statement.where(Category.is_active == True)

        count_statement = select(func.count()).select_from(statement.subquery())
        count_result = await session.execute(count_statement)
        count = count_result.scalar_one()

        offset = (pagination.page - 1) * pagination.size
        statement = statement.offset(offset).limit(pagination.size)
        result = await session.execute(statement)
        results = result.scalars().all()

        return results, count

    async def get(
        self,
        session: AsyncSession,
        id: int,
    ) -> Category | None:
        return await session.get(Category, id)

    async def create(
        self,
        session: AsyncSession,
        create_schema: CategoryCreate,
    ) -> Category:
        if await self.slug_exists(session, create_schema.slug):
            raise CustomRequestValidationError(
                [
                    {
                        "loc": ("body", "slug"),
                        "msg": "Category with this slug already exists.",
                        "type": "value_error",
                        "input": create_schema.slug,
                    }
                ]
            )

        category = Category(**create_schema.model_dump())
        session.add(category)
        await session.flush()
        return category

    async def slug_exists(
        self,
        session: AsyncSession,
        slug: str,
    ) -> bool:
        statement = select(Category).where(Category.slug == slug)
        result = await session.execute(statement)
        return result.scalar_one_or_none() is not None


category_service = CategoryService()
