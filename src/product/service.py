from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.common.pagination import Pagination
from src.exceptions import CustomRequestValidationError
from src.models import Product
from src.product.schemas import ProductCreate


class ProductService:

    async def list(
        self,
        session: AsyncSession,
        pagination: Pagination,
        category_id: int | None = None,
        active_only: bool = True,
        featured_only: bool = False,
    ) -> tuple[Sequence[Product], int]:
        statement = (
            select(Product)
            .options(selectinload(Product.category))
            .options(selectinload(Product.images))
        )
        
        if active_only:
            statement = statement.where(Product.is_active == True)
        if featured_only:
            statement = statement.where(Product.is_featured == True)
        if category_id:
            statement = statement.where(Product.category_id == category_id)

        count_statement = select(func.count()).select_from(statement.subquery())
        count_result = await session.execute(count_statement)
        count = count_result.scalar_one()

        offset = (pagination.page - 1) * pagination.size
        statement = statement.offset(offset).limit(pagination.size)
        result = await session.execute(statement)
        results = result.scalars().all()

        return results, count

    async def create(
            self,
            session: AsyncSession,
            create_schema: ProductCreate,
    ) -> Product:
        if await self.slug_exists(session, create_schema.slug):
            raise CustomRequestValidationError(
                [
                    {
                        "loc": ("body", "slug"),
                        "msg": "Product with this slug already exists.",
                        "type": "value_error",
                        "input": create_schema.slug,
                    }
                ]
            )

        product = Product(**create_schema.model_dump())
        session.add(product)
        await session.flush()
        await session.refresh(product, ["category"])
        return product

    async def slug_exists(
        self,
        session: AsyncSession,
        slug: str,
    ) -> bool:
        statement = select(Product).where(Product.slug == slug)
        result = await session.execute(statement)
        return result.scalar_one_or_none() is not None


product_service = ProductService()
