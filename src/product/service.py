from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.common.pagination import Pagination
from src.exceptions import BadRequest, CustomRequestValidationError, ResourceNotFound
from src.models import Product, ProductImage
from src.product.schemas import ProductCreate, ProductUpdate


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

    async def get(
        self,
        session: AsyncSession,
        id: int,
    ) -> Product | None:
        statement = (
            select(Product)
            .options(selectinload(Product.category))
            .options(selectinload(Product.images))
            .where(Product.id == id)
        )
        result = await session.execute(statement)
        return result.scalar_one_or_none()

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

    async def update(
            self,
            session: AsyncSession,
            product: Product,
            update_schema: ProductUpdate,
    ) -> Product:
        update_data = update_schema.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(product, key, value)

        session.add(product)
        await session.flush()
        return product

    async def delete(
            self,
            session: AsyncSession,
            product: Product,
    ) -> Product:
        await session.delete(product)
        await session.flush()
        return product

    async def get_image(
        self,
        session: AsyncSession,
        image_id: int,
    ) -> ProductImage | None:
        return await session.get(ProductImage, image_id)

    async def add_image(
        self,
        session: AsyncSession,
        product: Product,
        url: str,
    ) -> ProductImage:
        product_image = ProductImage(
            product_id=product.id,
            url=url,
            sort_order=len(product.images)
        )

        session.add(product_image)
        await session.flush()
        return product_image

    async def delete_image(
        self,
        session: AsyncSession,
        product_image: ProductImage,
    ) -> ProductImage:
        await session.delete(product_image)
        await session.flush()
        return product_image

    def validate_product_availability(
            self,
            requested_quantity: int,
            product: Product | None = None,
    ) -> None:
        if not product or not product.is_active:
            raise ResourceNotFound()
        if product.stock < requested_quantity:
            raise BadRequest("Insufficient stock.")

product_service = ProductService()
