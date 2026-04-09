from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.category.schemas import CategoryCreate
from src.common.pagination import Pagination
from src.exceptions import CustomRequestValidationError
from src.models.category import Category


class CategoryService:

    def create(
        self,
        session: Session,
        create_schema: CategoryCreate,
    ) -> Category:
        if self.slug_exists(session, create_schema.slug):
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
        session.flush()
        return category

    def slug_exists(
        self,
        session: Session,
        slug: str,
    ) -> bool:
        statement = select(Category).where(Category.slug == slug)
        result = session.execute(statement).scalar_one_or_none()
        return result is not None

    def list(
        self,
        session: Session,
        active_only: bool,
        pagination: Pagination,
    ) -> tuple[Sequence[Category], int]:
        statement = select(Category)

        if active_only:
            statement = statement.where(Category.is_active == True)

        count_statement = select(func.count()).select_from(statement.subquery())
        count = session.execute(count_statement).scalar_one()

        offset = (pagination.page - 1) * pagination.size
        statement = statement.offset(offset).limit(pagination.size)
        results = session.execute(statement).scalars().all()

        return results, count


category_service = CategoryService()
