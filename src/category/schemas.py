from pydantic import Field

from src.common.schemas import IDSchema, Schema, TimestampedSchema


class CategoryBase(Schema):
    name: str = Field(max_length=50)
    slug: str = Field(max_length=50)
    description: str | None = None
    is_active: bool = True
    sort_order: int = 0

class CategorySchema(CategoryBase, TimestampedSchema, IDSchema):
    pass

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(Schema):
    name: str | None = Field(default=None, max_length=50)
    description: str | None = Field(default=None, max_length=50)
    is_active: bool | None = None
    sort_order: int | None = None
