from pydantic import Field

from src.common.schemas import IDSchema, Schema, TimestampedSchema


class CategoryBase(Schema):
    name: str = Field(max_length=50)
    slug: str = Field(max_length=50)
    description: str | None = None
    is_active: bool = True
    sort_order: int = 0

class CategoryCreate(CategoryBase):
    pass

class CategorySchema(CategoryBase, IDSchema, TimestampedSchema):
    pass
