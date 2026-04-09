from sqlalchemy import select
from sqlalchemy.orm import Session

from src.category.schemas import CategoryCreate
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


category_service = CategoryService()
