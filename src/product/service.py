from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import CustomRequestValidationError
from src.models import Product
from src.product.schemas import ProductCreate


class ProductService:

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
